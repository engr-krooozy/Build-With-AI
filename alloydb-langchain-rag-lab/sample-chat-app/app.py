import streamlit as st
import requests
import os
import google.auth
import google.auth.transport.requests

# --- Configuration ---
# Get the RAG service URL from an environment variable
# This should be the URL of the Cloud Run service deployed in step 06.
RAG_SERVICE_URL_ENV = os.environ.get("RAG_SERVICE_URL")

# Try to get an identity token for authentication with the Cloud Run service
TOKEN = None
SERVICE_ACCOUNT_EMAIL = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_EMAIL") # Or use a specific SA for the app

try:
    # Attempt to get default credentials (useful if running on GCE with a service account)
    creds, project = google.auth.default(scopes=['openid', 'email', 'profile'])
    
    # If running with a service account that has Service Account Token Creator role,
    # or if the GCE metadata server can provide an identity token for the SA.
    # For Cloud Run, the service itself has an identity.
    # For local/GCE, need to ensure the SA has "Service Account Token Creator" role on itself,
    # or that the environment provides an identity token.
    
    # Check if we can get an ID token for the RAG_SERVICE_URL
    # This assumes the environment (e.g., GCE VM's service account) has permission to invoke the Cloud Run service.
    # Or, if running locally, `gcloud auth print-identity-token` would be used manually.
    # For an app on GCE calling another Cloud Run service, the GCE's SA needs `roles/run.invoker` on the target service.
    
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req) # Ensure credentials are valid

    # If the RAG_SERVICE_URL is available, try to get an ID token for it.
    # This is the most robust way for service-to-service authentication.
    if RAG_SERVICE_URL_ENV:
        TOKEN = creds.id_token # This might be a general ID token, better to target audience
        # For a more specific audience (the Cloud Run service URL):
        # This assumes the SA running this streamlit app has permission to generate tokens for this audience.
        # This is generally handled by the metadata server on GCP compute environments.
        # If running locally, `gcloud auth print-identity-token --audience={RAG_SERVICE_URL_ENV}`
        # For service-to-service, the SA of this app needs `roles/run.invoker` on the target Cloud Run service.
        # The `google.auth.default()` usually handles audience if the service account has the right permissions.
        # However, explicitly getting an ID token for an audience is cleaner if possible.
        # For simplicity here, we rely on the general ID token if available, or simply the existence of creds.
        # The `requests` call will use these credentials if available.
        # For Cloud Run to Cloud Run, it's automatic. For GCE to Cloud Run, the GCE SA needs invoker role.

except Exception as e:
    st.warning(f"Could not automatically obtain authentication credentials: {e}. "
               "If running locally and RAG_SERVICE_URL is set, ensure you are authenticated via `gcloud auth login` "
               "and `gcloud auth application-default login`. Manual token might be needed if errors persist.")
    TOKEN = None


# --- Helper Function to Call RAG Service ---
def get_rag_response(question: str, service_url: str):
    """Calls the /rag_answer endpoint of the RAG service."""
    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    payload = {"question": question}
    
    try:
        response = requests.post(f"{service_url}/rag_answer", json=payload, headers=headers, timeout=120) # Increased timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.Timeout:
        st.error("Request timed out. The RAG service might be slow to respond or starting up.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error calling RAG service: {e.response.status_code} {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling RAG service: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Streamlit App UI ---
st.set_page_config(page_title="AlloyDB RAG Chat", layout="wide")
st.title("💬 AlloyDB & LangChain RAG Chat Assistant")

st.sidebar.header("Configuration")
rag_service_url_input = st.sidebar.text_input(
    "RAG Service URL", 
    value=RAG_SERVICE_URL_ENV or "http://your-rag-service-url/please-set-env-variable",
    help="URL of the deployed RAG retrieval service on Cloud Run."
)

if not RAG_SERVICE_URL_ENV and rag_service_url_input.startswith("http://your-rag-service-url"):
    st.sidebar.warning("Please set the `RAG_SERVICE_URL` environment variable or enter it manually above.")
elif not rag_service_url_input:
     st.sidebar.error("RAG Service URL is not set. The application cannot function.")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "source_documents" in message and message["source_documents"]:
            with st.expander("Sources"):
                for doc in message["source_documents"]:
                    st.caption(f"Source: {doc.get('metadata', {}).get('source', 'N/A')}")
                    st.markdown(doc.get('page_content', ''))
                    st.markdown("---")


# React to user input
if prompt := st.chat_input("Ask me anything about your documents..."):
    if not rag_service_url_input or rag_service_url_input.startswith("http://your-rag-service-url"):
        st.error("RAG Service URL is not configured. Please set it in the sidebar or via environment variable.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            api_response = get_rag_response(prompt, rag_service_url_input)
            
            if api_response and "answer" in api_response:
                full_response = api_response["answer"]
                source_documents = api_response.get("source_documents", [])
                message_placeholder.markdown(full_response)
                
                if source_documents:
                    with st.expander("Sources"):
                        for doc in source_documents:
                            st.caption(f"Source: {doc.get('metadata', {}).get('source', 'N/A')}") # Assuming metadata might have a 'source' key
                            st.markdown(doc.get('page_content', ''))
                            st.markdown("---")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "source_documents": source_documents
                })
            elif api_response: # If response exists but no "answer" field
                message_placeholder.markdown("Sorry, I received an unexpected response from the RAG service.")
                st.session_state.messages.append({"role": "assistant", "content": "Unexpected response format."})
            else: # If api_response is None
                message_placeholder.markdown("Sorry, I couldn't get a response from the RAG service.")
                st.session_state.messages.append({"role": "assistant", "content": "Failed to get response."})

st.sidebar.markdown("---")
st.sidebar.markdown("This app demonstrates a RAG pipeline using AlloyDB, LangChain, and Vertex AI, all orchestrated via a Cloud Run service.")
st.sidebar.markdown("Ensure the RAG Service URL is correctly configured and the service is running.")
