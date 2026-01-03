# Building and Deploying Autonomous AI Agents (Cloud Run Edition)

## Welcome to the Workshop!

Welcome! In this hands-on workshop, you'll build **TravelGenie**, an autonomous AI travel concierge capable of planning complex itineraries, searching for flights, and booking hotels. You will learn how to build stateful AI agents using **LangGraph** and **Vertex AI (Gemini Pro)**, and deploy them as a scalable web application on **Google Cloud Run**.

This workshop is designed to be completed in approximately **1 hour**.

---

### What You'll Learn

*   How to set up a Google Cloud environment for AI development.
*   How to build an **Autonomous Agent** using **LangGraph** that can reason and decide which tools to use.
*   How to integrate **Gemini Pro** via Vertex AI as the reasoning engine.
*   How to give your agent access to the **Real-Time Internet** using DuckDuckGo Search.
*   How to build a chat interface using **Streamlit** that maintains full conversation memory.
*   How to containerize your application with **Docker**.
*   How to deploy your agent to **Cloud Run** for a serverless, scalable production environment.

### Our TravelGenie Architecture

The workflow is:
1.  **User Interaction:** The user chats with the Streamlit interface (e.g., "Plan a weekend trip to Paris").
2.  **Agent Orchestration:** The **LangGraph** agent receives the message history.
3.  **Reasoning:** **Gemini Pro** (Vertex AI) analyzes the request and decides if it needs to use tools (Web Search).
4.  **Tool Execution:** The agent executes the selected Python functions (e.g., searching DuckDuckGo for real flight prices).
5.  **Synthesis:** The agent sees the search results and generates a natural language response.

---

## Section 1: Preparing Your Google Cloud Environment (Approx. 10 mins)

First, let's get your Google Cloud project and Cloud Shell ready.

> **Prerequisite:** You need a Google Cloud account with billing enabled.

### 1.1. Activate Cloud Shell & Open Editor

*   **Action:** In the Google Cloud Console, click the **Activate Cloud Shell** button (`>_`).
*   **Action:** In the Cloud Shell terminal, click the **Open Editor** button to open the VS Code-like environment.

### 1.2. Configure Your Project and Region

```bash
# 1. Set your Project ID
# Replace `your-project-id` with your actual project ID
gcloud config set project your-project-id
echo "Project configured."
```

```bash
# 2. Store variables for easy use
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"

# 3. Confirm your settings
echo "Using Project ID: $PROJECT_ID in Region: $REGION"
```

### 1.3. Enable Required Google Cloud APIs

We need to enable the APIs for Vertex AI (for the model), Cloud Run (for hosting), and Cloud Build.

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com

echo "APIs enabled successfully."
```

---

## Section 2: Building the Agent Logic (Approx. 20 mins)

We will build our agent using `LangGraph`, a library for building stateful, multi-actor applications with LLMs.

### 2.1. Create the Project Directory

```bash
mkdir -p travel-genie
cd travel-genie
```

### 2.2. Create the Agent Code

This file contains the brain of our application. It defines the tools, the model connection, and the decision-making graph.

```bash
# Create agent.py
cat > agent.py << 'EOF'
import operator
from typing import Annotated, Sequence, TypedDict, Union

from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
import json
import random

# --- 1. Define Tools ---

# We use DuckDuckGo to search the real web for flight and hotel information
web_search = DuckDuckGoSearchRun(name="web_search")

@tool
def book_reservation(item_type: str, item_id: str, date: str) -> str:
    """Books a flight or hotel. item_type should be 'flight' or 'hotel'."""
    print(f"DEBUG: Booking {item_type} {item_id} for {date}")
    confirmation = f"CONF-{random.randint(1000, 9999)}"
    return f"Successfully booked {item_type} {item_id}. Confirmation code: {confirmation}"

# List of tools available to the agent
tools = [web_search, book_reservation]
tools_map = {t.name: t for t in tools}

# --- 2. Setup the Model ---

# We use Gemini 2.5 Pro via Vertex AI
# Ensure you are in a region that supports Gemini (us-central1 is standard)
model = ChatVertexAI(
    model_name="gemini-2.5-pro",
    temperature=0,
)

# Bind tools to the model so it knows they exist
model = model.bind_tools(tools)

# --- 3. Define the Graph State ---

class AgentState(TypedDict):
    # The state is just a list of messages (Human, AI, Tool)
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- 4. Define Nodes ---

def should_continue(state: AgentState):
    """Determines if the agent should continue (call a tool) or end (respond to user)."""
    last_message = state["messages"][-1]

    # If the LLM call resulted in no tool calls, we end
    if not last_message.tool_calls:
        return "end"

    # Otherwise, we continue to the 'action' node
    return "continue"

def call_model(state: AgentState):
    """Calls the Gemini model with the current history."""
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

def call_tool(state: AgentState):
    """Executes the tool requested by the model."""
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls

    results = []
    for t in tool_calls:
        print(f"Calling tool: {t['name']}")
        if t["name"] not in tools_map:
            result = "Error: Tool not found."
        else:
            # Execute the tool
            tool = tools_map[t["name"]]
            try:
                result = tool.invoke(t["args"])
            except Exception as e:
                result = f"Error executing tool: {e}"

        # Create a ToolMessage to communicate the result back to the model
        results.append(ToolMessage(tool_call_id=t["id"], content=str(result)))

    return {"messages": results}

# --- 5. Build the Graph ---

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

# Set entry point
workflow.set_entry_point("agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)

# Add normal edge from action back to agent (to interpret results)
workflow.add_edge("action", "agent")

# Compile the app
app = workflow.compile()
EOF
```

---

## Section 3: Building the User Interface (Approx. 15 mins)

We will use **Streamlit** to create a chat interface. We'll store the entire message history in the session state so the Agent remembers what it did (like searching for flights) when you ask a follow-up question.

### 3.1. Create the App Code

```bash
# Create app.py
cat > app.py << 'EOF'
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent import app as agent_app  # Import our compiled LangGraph app

st.set_page_config(page_title="TravelGenie 🧞", layout="centered")
st.title("TravelGenie: Your AI Concierge 🧞✈️")

# Helper function to extract text from mixed content
def get_message_text(msg):
    # Gemini sometimes returns a list of parts (text, thought_signature, etc.)
    if isinstance(msg.content, list):
        # Join all text parts
        return "".join([part.get("text", "") for part in msg.content if isinstance(part, dict) and part.get("type") == "text"])
    return msg.content

# Initialize chat history in session state as a list of LangChain Messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages (Filtered for Human and AI only)
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage) and message.content:
        # We only display the final text response, not the tool calls
        with st.chat_message("assistant"):
            st.markdown(get_message_text(message))

# Chat input
if prompt := st.chat_input("Where do you want to go?"):
    # 1. Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Add user message to state
    st.session_state.messages.append(HumanMessage(content=prompt))

    # 3. Run the Agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Run the graph with the full history
                # LangGraph returns the FINAL state of the graph
                inputs = {"messages": st.session_state.messages}
                result = agent_app.invoke(inputs)

                # Update session state with the full new history (including tool calls/outputs)
                st.session_state.messages = result["messages"]

                # Get the last message (the final answer)
                final_response = result["messages"][-1]

                if isinstance(final_response, AIMessage):
                    st.markdown(get_message_text(final_response))
                else:
                    st.write("Processing complete.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Sidebar instructions
with st.sidebar:
    st.header("How to use")
    st.markdown("""
    Ask TravelGenie to:
    - Search for flights (e.g., "Flights from NYC to London on Oct 10")
    - Find hotels (e.g., "Hotels in London under $200")
    - Book a trip (e.g., "Book the CloudAir flight")
    """)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
EOF
```

### 3.2. Create Requirements File

```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
streamlit
langchain>=0.2.0
langchain-core
langchain-community
langchain-google-vertexai
langgraph
google-cloud-aiplatform
ddgs
EOF
```

---

## Section 4: Containerization (Approx. 10 mins)

To run this on Google Cloud Run, we need to package our application into a Docker container.

### 4.1. Create the Dockerfile

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8080

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
EOF
```

---

## Section 5: Build and Deploy (Approx. 10 mins)

Now we will build the container image and deploy it to Cloud Run.

### 5.1. Build the Container Image

We use **Google Cloud Build** to build the image and store it in your project's artifact registry.

```bash
# Ensure you are in the travel-genie directory
# cd ~/travel-genie-workshop/travel-genie (if you aren't already there)

export IMAGE_NAME="gcr.io/${PROJECT_ID}/travel-genie:v1"

# Submit the build
gcloud builds submit --tag $IMAGE_NAME
```

### 5.2. Deploy to Cloud Run

Deploy the image as a serverless service.

```bash
gcloud run deploy travel-genie \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi
```

*   `--allow-unauthenticated`: Makes the app accessible via the public internet (great for workshops).
*   `--memory 1Gi`: Ensures enough RAM for the libraries.

### 5.3. Launch the App!

Once the command finishes, it will print a `Service URL` (e.g., `https://travel-genie-xyz.run.app`). Click that URL to open your TravelGenie app.

**Try this conversation flow:**
1.  *"Find me flights from San Francisco to Tokyo for next Monday."*
    *   *(The agent calls `search_flights` and shows options)*
2.  *"What hotels are available there?"*
    *   *(The agent knows "there" is Tokyo from the previous turn, calls `search_hotels`, and answers)*
3.  *"Book the cheapest flight for me."*
    *   *(The agent calls `book_reservation`)*

---

## Section 6: Making Changes & Updates

Development is an iterative process. If you want to modify your agent (e.g., add a new tool, change the prompt, or fix a bug in `app.py`), follow these steps to redeploy:

1.  **Modify the Code:** Edit your files in the Cloud Shell Editor.
2.  **Rebuild the Image:**
    ```bash
    gcloud builds submit --tag $IMAGE_NAME
    ```
3.  **Redeploy to Cloud Run:**
    ```bash
    gcloud run deploy travel-genie \
      --image $IMAGE_NAME \
      --platform managed \
      --region $REGION \
      --allow-unauthenticated \
      --memory 1Gi
    ```

Your changes will be live at the same URL!

---

## Section 7: Cleanup

To avoid ongoing charges, delete the resources when you are done.

```bash
# 1. Delete the Cloud Run Service
gcloud run services delete travel-genie --region=$REGION --quiet

# 2. Delete the Container Image
gcloud container images delete $IMAGE_NAME --quiet

echo "Cleanup complete."
```

---

## Appendix: Troubleshooting

*   **Quota Issues:** If you see errors regarding quotas for Vertex AI, ensure you are in a region where Gemini Pro is available (us-central1 is standard).
*   **Authentication:** Cloud Run uses the default service account. If you see "Permission Denied" for Vertex AI, ensure the "Compute Engine default service account" has the "Vertex AI User" role (though it typically does by default).
*   **App Errors:** Use the Cloud Console -> Cloud Run -> Logs tab to debug specific python errors.

**Happy Building!** 🚀
