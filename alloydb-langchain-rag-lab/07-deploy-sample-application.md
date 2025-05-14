# 7. Deploy and Test the Sample Chat Application

With the RAG retrieval service running on Cloud Run, you can now deploy a sample chat application to interact with it. This application will provide a user interface to ask questions and receive answers processed by your RAG pipeline.

For this lab, we'll run a simple Streamlit application directly on the GCE VM you prepared earlier. Streamlit allows us to quickly create an interactive web UI with Python.

All commands in this section for installing and running the Streamlit app should be executed **inside your GCE VM's SSH session**. Ensure you are in your Python virtual environment (`.venv-alloydb-rag`).

## 1. Understanding the Sample Chat Application

The sample application (`sample-chat-app/app.py`) is a Streamlit web application that:
*   Provides a text input for users to ask questions.
*   Displays the chat history, including user questions and assistant answers.
*   When a user submits a question:
    *   It makes an HTTP POST request to the `/rag_answer` endpoint of your deployed RAG retrieval service on Cloud Run.
    *   It sends the question in the request body.
    *   It includes an Identity Token from the GCE VM's service account in the `Authorization` header to authenticate with the Cloud Run service.
    *   It displays the answer and any retrieved source documents returned by the RAG service.
*   It reads the RAG service URL from an environment variable `RAG_SERVICE_URL`.

## 2. Prepare the Application Code and Environment on GCE VM

The necessary Python script (`app.py`) and requirements file (`requirements_app.txt`) for the Streamlit application should have been created in the `alloydb-langchain-rag-lab/sample-chat-app/` directory in the previous steps.

*   **Navigate to the sample app directory on your GCE VM:**
    If you're not already there from previous steps within the GCE VM's SSH session:
    ```bash
    # Assuming your project's root directory is ~/alloydb-langchain-rag-lab on the VM
    # If you cloned it elsewhere, adjust the path.
    # For this lab, we are creating files directly, so ensure you are in the correct path.
    cd ~/alloydb-langchain-rag-lab/sample-chat-app 
    # If you haven't created these files on the VM yet, you would transfer them (e.g. using gcloud compute scp) 
    # or recreate them using `nano` or `vim` with the content provided in the previous step.
    ```
    For this codelab, we assume the files `app.py` and `requirements_app.txt` are already in `/app/alloydb-langchain-rag-lab/sample-chat-app/` in the development environment, and you'll be running commands from the GCE VM that has access to this path (e.g. if /app is a mounted drive or if you `git clone` the repo onto the VM).

*   **Ensure your Python virtual environment is active:**
    ```bash
    source ~/.venv-alloydb-rag/bin/activate 
    # Or source .venv-alloydb-rag/bin/activate if you created it in the project directory
    ```

*   **Install Streamlit and other dependencies:**
    ```bash
    pip install -r requirements_app.txt
    ```
    This will install Streamlit and the `requests` library.

## 3. Run the Streamlit Chat Application

*   **Set the RAG Service URL Environment Variable:**
    The Streamlit app needs to know the URL of your deployed RAG retrieval service. You obtained this URL at the end of section 06.
    ```bash
    # In your GCE VM's SSH session:
    export RAG_SERVICE_URL="YOUR_CLOUD_RUN_SERVICE_URL" 
    # Replace YOUR_CLOUD_RUN_SERVICE_URL with the actual URL from the previous step.
    # e.g., https://alloydb-rag-service-xxxxxxxxxx-uc.a.run.app

    echo "RAG Service URL set to: ${RAG_SERVICE_URL}"
    ```
    If you don't set this, the app will prompt you to enter it in its sidebar.

*   **Start the Streamlit Application:**
    ```bash
    streamlit run app.py --server.port 8080
    ```
    *   `--server.port 8080`: Runs Streamlit on port 8080. You can choose another port if 8080 is in use, but you'll need to adjust the Web Preview settings accordingly.

    You should see output similar to:
    ```
    You can now view your Streamlit app in your browser.

    Network URL: http://<VM_EXTERNAL_IP>:8080
    External URL: http://<VM_EXTERNAL_IP>:8080
    ```
    Do **not** use these URLs directly from your local browser yet, as the VM's firewall might block access. We'll use Cloud Shell's Web Preview.

## 4. Access the Chat Application via Cloud Shell Web Preview

Google Cloud Shell's Web Preview feature allows you to securely access web applications running on your GCE VM through a proxy.

*   **Ensure your Streamlit app is running on the GCE VM (from the previous step).**
*   **In your Google Cloud Shell window (not the GCE VM's SSH session):**
    Click on the **Web preview** button (looks like an eye icon or a rectangle with an arrow) on the top right of the Cloud Shell toolbar.
*   Select **Change port**.
*   Enter `8080` (or the port you used for Streamlit) and click **Change and Preview**.

A new browser tab will open, proxying to your Streamlit application running on the GCE VM. You should see the "AlloyDB RAG Chat Assistant" interface.

## 5. Test the End-to-End RAG Functionality

Now you can interact with your RAG system:

1.  **Wait for Data Loading (Important Prerequisite - Manual Step for this Lab):**
    *   This codelab guide focuses on deploying the infrastructure and applications. **It does not yet include a dedicated step for loading and embedding your actual documents into the AlloyDB database.**
    *   For the RAG application to provide meaningful, context-aware answers, you must first populate the `langchain_pg_embedding` table in your `rag_lab_db` database with your text documents and their corresponding vector embeddings.
    *   You can achieve this by:
        *   Creating a Python script (run on the GCE VM) that reads your documents (e.g., from text files, PDFs, or other sources).
        *   Uses LangChain's document loaders and text splitters.
        *   Uses `VertexAIEmbeddings` (or `AlloyDBEmbeddings`) to generate embeddings.
        *   Uses the `PGVector` store's `add_texts()` or `add_documents()` method to store them in AlloyDB. The RAG service also has an example `/add_texts` endpoint you could adapt or call.
    *   **Without this data loading step, the RAG service will only have access to the LLM's general knowledge, not your specific documents.**

2.  **Ask Questions:**
    *   Once you have loaded data, type a question into the chat input field in the Streamlit app (e.g., "What are the key features of AlloyDB AI?" if you loaded documents about AlloyDB).
    *   The Streamlit app will send your question to the RAG service on Cloud Run.
    *   The RAG service will query AlloyDB for relevant documents, use the LLM to generate an answer based on those documents, and return it.
    *   The answer and any source documents should appear in the chat interface.

3.  **Troubleshooting:**
    *   **Check GCE VM Logs:** If Streamlit fails, check its output in the GCE VM's SSH terminal.
    *   **Check RAG Service Logs:** Go to Cloud Run in the Google Cloud Console, find your `alloydb-rag-service`, and check its logs for any errors if the Streamlit app reports issues connecting or getting responses. This is crucial for diagnosing problems with database connections, API calls to Vertex AI, or permissions.
    *   **Verify RAG Service URL:** Double-check that the `RAG_SERVICE_URL` environment variable on the GCE VM is correct.
    *   **Authentication:** The Streamlit app attempts to get an identity token. Ensure the GCE VM's service account (`gce-alloydb-rag-sa`) has the `roles/run.invoker` permission on the `alloydb-rag-service` Cloud Run service. This was set up in step 04, but it's good to verify if you encounter permission errors.

You have now deployed and tested a full, albeit simple, RAG pipeline using AlloyDB AI, LangChain, Cloud Run, and a Streamlit frontend on a GCE VM. The next steps would involve refining the data ingestion process, exploring more advanced LangChain features, and potentially enhancing the application's robustness and UI.
