# 3. Deploy AlloyDB Cluster

This section guides you through deploying an AlloyDB cluster. AlloyDB is a fully managed, PostgreSQL-compatible database service that offers high performance, availability, and scalability. For this lab, we will configure it to leverage AlloyDB AI for vector embeddings and similarity search.

Make sure you have set your `PROJECT_ID` and `REGION` environment variables as described in the "Before You Begin" section.

## 1. Configure Private IP Range for VPC Peering

AlloyDB clusters reside within a Virtual Private Cloud (VPC) network and require a private IP address range for communication. We'll set up VPC Peering to allow services within your VPC to connect to AlloyDB.

*   **Note:** This step is only required if you haven't already configured a private IP range for Google services in your default VPC network. If you have an existing setup, you might be able to skip this.

*   Create a private IP address range:
    ```bash
    gcloud compute addresses create psa-range \
        --global \
        --purpose=VPC_PEERING \
        --prefix-length=24 \
        --description="VPC private service access for AlloyDB" \
        --network=default \
        --project=${PROJECT_ID}
    ```
    This command reserves an IP range named `psa-range` in your `default` VPC network.

*   Create a private connection using the allocated IP range:
    ```bash
    gcloud services vpc-peerings connect \
        --service=servicenetworking.googleapis.com \
        --ranges=psa-range \
        --network=default \
        --project=${PROJECT_ID}
    ```
    This command establishes a peering connection between your VPC and Google services. This operation can take a couple of minutes to complete.

    Expected output for both commands will confirm the creation or update of the resources.

## 2. Set Up AlloyDB Cluster and Instance

Now, let's create the AlloyDB cluster and a primary instance.

*   **Define a password for the `postgres` superuser:**
    It's crucial to set a strong password. You can define your own or generate one:
    ```bash
    export PGPASSWORD=$(openssl rand -base64 12)
    echo "Your AlloyDB password is: ${PGPASSWORD}"
    ```
    **Important:** Note down this password securely. You will need it to connect to the database.

*   **Define AlloyDB Cluster Name:**
    ```bash
    export ADBCLUSTER=alloydb-rag-cluster
    echo "AlloyDB Cluster Name: ${ADBCLUSTER}"
    ```

*   **Create the AlloyDB Cluster:**
    This command creates the cluster. We'll use the `us-central1` region defined by the `$REGION` environment variable.
    ```bash
    gcloud alloydb clusters create ${ADBCLUSTER} \
        --password=${PGPASSWORD} \
        --network=default \
        --region=${REGION} \
        --project=${PROJECT_ID}
    ```
    This process can take several minutes. You'll see an operation ID and a success message upon completion.

*   **Create the AlloyDB Primary Instance:**
    Once the cluster is created, you need to add a primary instance to it.
    ```bash
    export ADBINSTANCE=${ADBCLUSTER}-pr1
    echo "AlloyDB Primary Instance Name: ${ADBINSTANCE}"

    gcloud alloydb instances create ${ADBINSTANCE} \
        --instance-type=PRIMARY \
        --cpu-count=2 \
        --region=${REGION} \
        --cluster=${ADBCLUSTER} \
        --project=${PROJECT_ID}
        # For higher availability, consider --availability-type=REGIONAL
        # For this lab, the default (ZONAL) is sufficient.
    ```
    This command creates a primary instance with 2 vCPUs. Instance creation can take 10-15 minutes.

    *   **Note on AlloyDB AI:** AlloyDB AI features, including vector support via `google_ml_integration` and extensions like `pgvector`, are typically enabled and configured *after* the instance is running by connecting to the database and running SQL commands. We will cover this in the "Initialize the Database" section (05-initialize-database.md). No specific flags for AlloyDB AI are needed during cluster or instance creation itself.

## 3. Verify Cluster and Instance Creation

You can verify that your cluster and instance have been created successfully:

*   List your AlloyDB clusters:
    ```bash
    gcloud alloydb clusters list --region=${REGION} --project=${PROJECT_ID}
    ```
*   Describe your cluster:
    ```bash
    gcloud alloydb clusters describe ${ADBCLUSTER} --region=${REGION} --project=${PROJECT_ID}
    ```
*   List instances in your cluster:
    ```bash
    gcloud alloydb instances list --cluster=${ADBCLUSTER} --region=${REGION} --project=${PROJECT_ID}
    ```
*   Describe your primary instance and note its IP address (you'll need this later):
    ```bash
    gcloud alloydb instances describe ${ADBINSTANCE} --cluster=${ADBCLUSTER} --region=${REGION} --project=${PROJECT_ID}
    ```
    Look for the `ipAddress` in the output. You can also store it in an environment variable:
    ```bash
    export ADB_INSTANCE_IP=$(gcloud alloydb instances describe ${ADBINSTANCE} --cluster=${ADBCLUSTER} --region=${REGION} --project=${PROJECT_ID} --format="value(ipAddress)")
    echo "AlloyDB Instance IP: ${ADB_INSTANCE_IP}"
    ```

With the AlloyDB cluster and primary instance deployed, you are ready to prepare the virtual machine that will interact with it.
