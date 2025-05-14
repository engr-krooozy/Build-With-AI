# 8. Clean Up Environment

To avoid incurring ongoing charges for the Google Cloud resources used in this codelab, it's important to clean them up. If you created a new project specifically for this lab, you can simply delete the project. Otherwise, delete the individual resources as described below.

All commands in this section should be run from your **Google Cloud Shell**. Ensure your `PROJECT_ID` and `REGION` environment variables are set, or replace them with your actual values.

## 1. Define Environment Variables (If Not Already Set)

If you have a new Cloud Shell session, or if your environment variables are no longer set, redefine them to ensure the cleanup commands target the correct resources.
```bash
export PROJECT_ID="YOUR_PROJECT_ID" # Replace with your Project ID
export REGION="us-central1"       # Or the region you used
export ZONE="${REGION}-a"           # Or the zone you used

# Names used during creation (replace if you used different names)
export GCE_INSTANCE_NAME="alloydb-rag-vm"
export GCE_SERVICE_ACCOUNT_NAME="gce-alloydb-rag-sa"

export ADBCLUSTER="alloydb-rag-cluster"
export ADBINSTANCE="${ADBCLUSTER}-pr1" # As defined in step 03

export AR_REPO_NAME="alloydb-rag-service-repo"
export CLOUD_RUN_SERVICE_NAME="alloydb-rag-service"
export CLOUD_RUN_SA_NAME="cloud-run-rag-sa"
export VPC_CONNECTOR_NAME="rag-lab-connector"

echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Zone: ${ZONE}"
# Add echoes for other variables if you want to verify them
```
**Important:** Double-check these variable values to match what you used during the lab to prevent accidental deletion of other resources.

## 2. Delete the Cloud Run Service

*   Delete the RAG retrieval service:
    ```bash
    gcloud run services delete ${CLOUD_RUN_SERVICE_NAME} \
        --platform=managed \
        --region=${REGION} \
        --project=${PROJECT_ID} \
        --quiet
    ```
    Confirm when prompted, if not using `--quiet`.

## 3. Delete the Cloud Run Service Account

*   Delete the service account used by the Cloud Run service:
    ```bash
    gcloud iam service-accounts delete ${CLOUD_RUN_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
        --project=${PROJECT_ID} \
        --quiet
    ```

## 4. Delete the GCE VM Instance

*   Delete the Google Compute Engine VM:
    ```bash
    gcloud compute instances delete ${GCE_INSTANCE_NAME} \
        --zone=${ZONE} \
        --project=${PROJECT_ID} \
        --quiet
    ```

## 5. Delete the GCE VM Service Account

*   Delete the service account used by the GCE VM:
    ```bash
    gcloud iam service-accounts delete ${GCE_SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
        --project=${PROJECT_ID} \
        --quiet
    ```

## 6. Delete the Serverless VPC Access Connector

*   Delete the VPC Access connector:
    ```bash
    gcloud compute networks vpc-access connectors delete ${VPC_CONNECTOR_NAME} \
        --region=${REGION} \
        --project=${PROJECT_ID} \
        --quiet
    ```
    This can take a few minutes.

## 7. Delete the AlloyDB Cluster and Instances

*   **Delete the AlloyDB Cluster (which includes its primary instance):**
    Using the `--force` flag will also delete any primary or read pool instances associated with the cluster.
    ```bash
    gcloud alloydb clusters delete ${ADBCLUSTER} \
        --region=${REGION} \
        --project=${PROJECT_ID} \
        --force \
        --quiet
    ```
    This operation can take several minutes. `--force` helps avoid errors if instances are still attached.

*   **Verify and Delete AlloyDB Backups (Optional but Recommended):**
    While automatic backups are typically deleted with the cluster when `--force` is used, and on-demand backups might also be, it's good practice to check.
    ```bash
    echo "Listing backups for cluster projects/${PROJECT_ID}/locations/${REGION}/clusters/${ADBCLUSTER}..."
    gcloud alloydb backups list \
        --region=${REGION} \
        --project=${PROJECT_ID} \
        --filter="clusterName:projects/${PROJECT_ID}/locations/${REGION}/clusters/${ADBCLUSTER}" --format="value(name)"

    # If any backups are listed and you want to delete them:
    # for backup_name in $(gcloud alloydb backups list --region=${REGION} --project=${PROJECT_ID} --filter="clusterName:projects/${PROJECT_ID}/locations/${REGION}/clusters/${ADBCLUSTER}" --format="value(name)" --sort-by=~createTime); do
    #   echo "Deleting backup: $(basename ${backup_name})..."
    #   gcloud alloydb backups delete $(basename ${backup_name}) --region ${REGION} --project=${PROJECT_ID} --quiet
    # done
    ```
    *Uncomment and run the loop if you find backups you wish to delete.*

## 8. Delete the Artifact Registry Repository

*   Delete the Docker repository:
    ```bash
    gcloud artifacts repositories delete ${AR_REPO_NAME} \
        --location=${REGION} \
        --project=${PROJECT_ID} \
        --quiet
    ```

## 9. Delete Private IP Range for VPC Peering (Use with Caution)

The private IP range (`psa-range`) created for VPC Service Peering might be used by other services. **Only delete it if you are sure it's not needed by anything else.**

*   **Check active VPC peerings:**
    ```bash
    gcloud services vpc-peerings list --network=default --project=${PROJECT_ID}
    ```
    If the peering for `servicenetworking.googleapis.com` using `psa-range` is listed and you are sure you want to remove it:
    ```bash
    # gcloud services vpc-peerings delete \
    #     --service=servicenetworking.googleapis.com \
    #     --network=default \
    #     --project=${PROJECT_ID}
    # This command is commented out due to its potential impact. Uncomment if you are certain.
    ```

*   **Delete the reserved IP address range:**
    If you are certain the range is no longer needed by any peering:
    ```bash
    # gcloud compute addresses delete psa-range \
    #     --global \
    #     --project=${PROJECT_ID} \
    #     --quiet
    # This command is commented out due to its potential impact. Uncomment if you are certain.
    ```
    **It's often safer to leave the `psa-range` if you have other Google services using VPC peering in the `default` network.**

## 10. Disabling APIs

Disabling APIs is generally not required if you delete the resources using them or if you intend to delete the project. If you are not deleting the project and want to disable the specific APIs enabled:
```bash
# gcloud services disable alloydb.googleapis.com --project=${PROJECT_ID}
# gcloud services disable aiplatform.googleapis.com --project=${PROJECT_ID}
# gcloud services disable run.googleapis.com --project=${PROJECT_ID}
# gcloud services disable vpcaccess.googleapis.com --project=${PROJECT_ID}
# ... and so on for other APIs enabled in step 02.
```
This is usually an optional step if resources are properly deleted.

## 11. Delete the Project (Optional)

If you created a Google Cloud project specifically for this codelab, you can delete the entire project to remove all resources and stop all billing.

*   **To delete the project:**
    ```bash
    # gcloud projects delete ${PROJECT_ID}
    ```
    **Warning:** This action is irreversible and will delete all resources within the project. Ensure you have backed up anything important.

By following these steps, you can ensure that all resources created during this codelab are properly removed, preventing any unexpected charges. Always double-check the names and IDs of resources before deletion.
