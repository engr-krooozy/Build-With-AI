# Before You Begin

This section details the initial configurations and setup steps you must complete in your Google Cloud environment before proceeding with the core parts of the codelab.

## 1. Set Your Project ID

Ensure your Google Cloud Shell session is configured to use your desired project.

*   Verify your active project:
    ```bash
    gcloud config get-value project
    ```
*   If you need to set it, use the following command, replacing `[YOUR-PROJECT-ID]` with your actual Project ID:
    ```bash
    gcloud config set project [YOUR-PROJECT-ID]
    ```

## 2. Set Environment Variables

To streamline commands throughout the codelab, set the following environment variables in your Cloud Shell.

*   **Project ID:**
    ```bash
    export PROJECT_ID=$(gcloud config get-value project)
    echo "PROJECT_ID=${PROJECT_ID}"
    ```
*   **Region:** This codelab will primarily use `us-central1`. If you plan to use a different region, ensure all services support it.
    ```bash
    export REGION=us-central1
    echo "REGION=${REGION}"
    ```
*   **Zone:** For services requiring a zone within the region (like Compute Engine).
    ```bash
    export ZONE=${REGION}-a
    echo "ZONE=${ZONE}"
    ```

    *Note: You might need to adjust these variables if you are using a pre-existing setup or have specific regional requirements.*

## 3. Enable Required Google Cloud APIs

You need to enable several Google Cloud APIs to allow your project to use the necessary services.

*   Run the following command to enable all required APIs:
    ```bash
    gcloud services enable \
        alloydb.googleapis.com \
        compute.googleapis.com \
        aiplatform.googleapis.com \
        run.googleapis.com \
        cloudresourcemanager.googleapis.com \
        servicenetworking.googleapis.com \
        vpcaccess.googleapis.com \
        cloudbuild.googleapis.com \
        artifactregistry.googleapis.com \
        iam.googleapis.com
    ```
*   This command enables:
    *   **AlloyDB API (`alloydb.googleapis.com`):** For creating and managing AlloyDB clusters and instances.
    *   **Compute Engine API (`compute.googleapis.com`):** For creating and managing Virtual Machines (VMs) that will host our application and tools.
    *   **Vertex AI API (`aiplatform.googleapis.com`):** For accessing Google's unified machine learning platform, which we'll use for embeddings and potentially model hosting.
    *   **Cloud Run API (`run.googleapis.com`):** For deploying containerized applications, such as our retrieval service.
    *   **Cloud Resource Manager API (`cloudresourcemanager.googleapis.com`):** For managing project metadata and resources.
    *   **Service Networking API (`servicenetworking.googleapis.com`):** For managing private network connections for services like AlloyDB.
    *   **VPC Access API (`vpcaccess.googleapis.com`):** For connecting serverless environments (like Cloud Run) to your VPC network.
    *   **Cloud Build API (`cloudbuild.googleapis.com`):** For building container images.
    *   **Artifact Registry API (`artifactregistry.googleapis.com`):** For storing and managing container images.
    *   **Identity and Access Management (IAM) API (`iam.googleapis.com`):** For managing permissions and service accounts.

    You should see an "Operation "..." finished successfully." message for each enabled API, or a message indicating it's already enabled.

    *A note on costs: Please be aware that enabling and using these services may incur costs if you are not within the Google Cloud Free Tier or promotional offers. Review the pricing for each service and ensure it's acceptable for you. You can typically manage costs by deleting resources after completing the lab.*

Once these steps are completed, your Google Cloud environment is prepared for the subsequent parts of this codelab.
