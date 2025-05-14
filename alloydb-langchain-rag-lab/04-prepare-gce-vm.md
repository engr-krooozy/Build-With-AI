# 4. Prepare GCE Virtual Machine

We will use a Google Compute Engine (GCE) virtual machine (VM) to host our Python application, the LangChain components, and the tools needed to interact with AlloyDB and other Google Cloud services.

Ensure your `PROJECT_ID`, `REGION`, and `ZONE` environment variables are set as described in "02-Before You Begin".

## 1. Create a Service Account for the VM

A service account provides an identity for your VM, allowing it to securely access Google Cloud APIs with specific permissions.

*   Define a name for your service account:
    ```bash
    export GCE_SERVICE_ACCOUNT_NAME="gce-alloydb-rag-sa"
    echo "GCE Service Account Name: ${GCE_SERVICE_ACCOUNT_NAME}"
    ```

*   Create the service account:
    ```bash
    gcloud iam service-accounts create ${GCE_SERVICE_ACCOUNT_NAME} \
        --description="Service Account for GCE VM in AlloyDB RAG Lab" \
        --display-name="AlloyDB RAG Lab VM SA" \
        --project=${PROJECT_ID}
    ```

*   Grant necessary roles to the service account. These roles allow the VM to interact with various Google Cloud services:
    ```bash
    # Role for general Google Cloud API access, including Vertex AI
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/aiplatform.user"

    # Role for interacting with AlloyDB (e.g., getting instance details)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/alloydb.client" # More specific than alloydb.viewer

    # Role for Cloud Run (if deploying services from the VM, or interacting with them)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/run.invoker" # Or roles/run.admin if more control is needed

    # Roles for Cloud Build and Artifact Registry (if building/storing containers from VM)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/cloudbuild.builds.editor"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/artifactregistry.writer" # To push images

    # Role for Service Account User (allows the GCE instance to impersonate this SA)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
      --member="serviceAccount:${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
      --role="roles/iam.serviceAccountUser"

    # Role for Service Usage Consumer (to enable APIs if needed from the VM)
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
      --member="serviceAccount:${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
      --role="roles/serviceusage.serviceUsageConsumer"
    ```
    *Note: The roles granted are based on potential actions performed during the lab. Adjust as necessary for your specific security requirements.*

## 2. Deploy the GCE VM

Now, create the GCE VM instance.

*   Define a name for your VM instance:
    ```bash
    export GCE_INSTANCE_NAME="alloydb-rag-vm"
    echo "GCE Instance Name: ${GCE_INSTANCE_NAME}"
    ```

*   Create the VM instance:
    We'll use a Debian 12 image and an e2-medium machine type, which provides a good balance of resources for this lab.
    ```bash
    gcloud compute instances create ${GCE_INSTANCE_NAME} \
        --project=${PROJECT_ID} \
        --zone=${ZONE} \
        --machine-type=e2-medium \
        --image-family=debian-12 \
        --image-project=debian-cloud \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        --service-account=${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
        --create-disk=auto-delete=yes,boot=yes
    ```
    *   `--scopes=https://www.googleapis.com/auth/cloud-platform`: Grants the VM broad access to Google Cloud services, controlled by the IAM roles of its service account.
    *   `--service-account`: Assigns the service account created in the previous step to this VM.

    This command will take a few minutes to complete. You'll see the VM's external IP and other details upon successful creation.

## 3. Connect to the VM via SSH

Once the VM is running, connect to it using SSH through `gcloud`.

```bash
gcloud compute ssh ${GCE_INSTANCE_NAME} --zone=${ZONE} --project=${PROJECT_ID}
```
*   The first time you connect, `gcloud` may generate SSH keys for you.
*   You will now be logged into the shell of your GCE VM. All subsequent commands in the "Install Software on VM" section should be run *inside this VM shell*.

## 4. Install Software on the VM

Inside your VM's SSH session, update the package lists and install necessary software.

*   Update package manager and install common tools:
    ```bash
    sudo apt-get update
    sudo apt-get install -y \
        postgresql-client \
        python3 \
        python3-pip \
        python3.11-venv \
        git \
        curl \
        unzip
    ```
    This installs:
    *   `postgresql-client`: The `psql` command-line tool for interacting with AlloyDB.
    *   `python3` & `python3-pip`: Python 3 and its package installer, pip. Debian 12 typically includes Python 3.11.
    *   `python3.11-venv`: Specifically for creating Python 3.11 virtual environments.
    *   `git`: For cloning repositories.
    *   `curl`: For downloading files or testing HTTP endpoints.
    *   `unzip`: For extracting zip files.

*   Verify Python and pip versions (optional):
    ```bash
    python3 --version
    pip3 --version
    ```
    You should see versions for Python 3.11.x and a recent pip version.

## 5. Set up Python Virtual Environment (Recommended)

It's good practice to use a Python virtual environment to manage project dependencies.

*   Create and activate a virtual environment (still inside the VM's SSH session):
    ```bash
    python3 -m venv .venv-alloydb-rag
    source .venv-alloydb-rag/bin/activate
    ```
    Your shell prompt should now be prefixed with `(.venv-alloydb-rag)`, indicating the virtual environment is active.

*   Upgrade pip within the virtual environment:
    ```bash
    pip install --upgrade pip
    ```

Your GCE VM is now prepared with the necessary tools and a Python environment. You can proceed to the next steps of the codelab, which will involve interacting with your AlloyDB instance from this VM. Remember to exit the SSH session (`exit`) when you are done working directly on the VM.
