# 5. Initialize the Database

This section covers connecting to your AlloyDB instance from the GCE VM, creating a dedicated database, and enabling the necessary PostgreSQL extensions for building our RAG application with LangChain and AlloyDB AI.

All commands in this section should be run from your GCE VM's SSH session, preferably within the activated Python virtual environment (`.venv-alloydb-rag`) as it might be used for subsequent Python scripting for data loading.

## 1. Connect to Your AlloyDB Instance

You'll use `psql`, the PostgreSQL command-line client, which you installed on the GCE VM in the previous step.

*   **Ensure Environment Variables are Set:**
    If you have disconnected from your GCE VM and reconnected, or if the environment variables are not set, ensure the following are defined in your VM's shell. You noted these during the AlloyDB cluster setup:
    ```bash
    # You should have noted this password when creating the AlloyDB cluster
    export PGPASSWORD="YOUR_ALLOYDB_PASSWORD" 
    # This IP was noted after the AlloyDB instance became ready
    export ADB_INSTANCE_IP="YOUR_ALLOYDB_INSTANCE_IP" 
    # The default user for AlloyDB
    export ADB_USER="postgres"
    
    # Verify them (optional)
    echo "Connecting to AlloyDB instance at ${ADB_INSTANCE_IP} as user ${ADB_USER}"
    ```
    Replace `YOUR_ALLOYDB_PASSWORD` and `YOUR_ALLOYDB_INSTANCE_IP` with the actual values for your AlloyDB instance.

*   **Connect to the default `postgres` database to create a new database:**
    ```bash
    psql "host=${ADB_INSTANCE_IP} user=${ADB_USER} sslmode=require" -c "CREATE DATABASE rag_lab_db;"
    ```
    This command connects to the instance and issues a `CREATE DATABASE` command. `sslmode=require` is recommended for secure connections.
    You should see `CREATE DATABASE` as output.

    *Note on AlloyDB Auth Proxy:* For connections from outside the VPC (e.g., local development) or for enhanced security, using the [AlloyDB Auth Proxy](https://cloud.google.com/alloydb/docs/auth-proxy/overview) is a best practice. However, for this lab, connecting from a GCE VM within the same VPC and region, direct psql connection with SSL is generally acceptable.

## 2. Enable Required Extensions

Connect to your newly created database and enable the `vector` and `google_ml_integration` extensions.

*   **Define your new database name as an environment variable (optional, for convenience):**
    ```bash
    export ADB_DATABASE="rag_lab_db"
    echo "Using database: ${ADB_DATABASE}"
    ```

*   **Connect to the `rag_lab_db` database and enable extensions:**
    ```bash
    psql "host=${ADB_INSTANCE_IP} user=${ADB_USER} dbname=${ADB_DATABASE} sslmode=require" -c "CREATE EXTENSION IF NOT EXISTS vector;"
    psql "host=${ADB_INSTANCE_IP} user=${ADB_USER} dbname=${ADB_DATABASE} sslmode=require" -c "CREATE EXTENSION IF NOT EXISTS google_ml_integration;"
    ```
    You should see `CREATE EXTENSION` as output for each command (or a notice if they already exist).
    *   **`vector` (pgvector):** This extension provides the `vector` data type and functions for similarity search (e.g., HNSW indexing, L2 distance, cosine similarity). LangChain's `PGVector` vector store will use this.
    *   **`google_ml_integration`:** This is a key part of AlloyDB AI. It allows the database to call out to Vertex AI models, including models for generating text embeddings. This means you can generate embeddings for your text data directly within SQL if needed, or have LangChain leverage these capabilities.

## 3. Create Tables for Documents and Embeddings

For a RAG application, you need to store your text documents (or chunks of them) and their corresponding vector embeddings. LangChain's `PGVector` can automatically create tables, but for clarity and control, we can define them.

The typical schema used by LangChain's `PGVector` includes:
*   `langchain_pg_collection`: Stores metadata about different collections of documents.
*   `langchain_pg_embedding`: Stores the actual documents, their embeddings, and metadata.

Let's create these tables with appropriate columns. We'll assume an embedding dimension of 768, which is common for models like `textembedding-gecko`. Adjust `vector(768)` if you plan to use a model with different embedding dimensions.

*   **Connect to your database and execute the following SQL commands:**
    You can do this by entering `psql "host=${ADB_INSTANCE_IP} user=${ADB_USER} dbname=${ADB_DATABASE} sslmode=require"` to start an interactive session, then pasting the SQL commands, or by using multiple `-c` flags.

    ```sql
    -- Start an interactive psql session (recommended for multi-line SQL)
    psql "host=${ADB_INSTANCE_IP} user=${ADB_USER} dbname=${ADB_DATABASE} sslmode=require"

    -- Inside psql, execute the following:

    -- Create a table for collections (optional but good for organizing multiple RAG sources)
    CREATE TABLE IF NOT EXISTS langchain_pg_collection (
        uuid UUID PRIMARY KEY,
        name VARCHAR(255) UNIQUE,
        cmetadata JSONB
    );

    -- Create the main table for documents and their embeddings
    CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
        uuid UUID PRIMARY KEY,
        collection_id UUID REFERENCES langchain_pg_collection(uuid) ON DELETE CASCADE,
        embedding VECTOR(768), -- Adjust 768 to your embedding model's dimension
        document TEXT,
        cmetadata JSONB
    );

    -- Create an index for efficient similarity search on the embeddings
    -- Using HNSW index with cosine distance, common for pgvector
    CREATE INDEX IF NOT EXISTS langchain_pg_embedding_embedding_idx 
    ON langchain_pg_embedding 
    USING HNSW (embedding vector_cosine_ops); 
    -- Or using IVFFlat: CREATE INDEX ON langchain_pg_embedding USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

    -- Exit psql session
    \q
    ```

    **Explanation:**
    *   `langchain_pg_collection`: This table can store information about different sets of documents you might use. For a single source, you might have one entry here.
    *   `langchain_pg_embedding`:
        *   `uuid`: A unique ID for each embedding entry.
        *   `collection_id`: Links to the `langchain_pg_collection` table.
        *   `embedding`: Stores the vector embedding. The `VECTOR(768)` type comes from the `vector` extension. **Ensure the dimension (768) matches the output dimension of the embedding model you will use.**
        *   `document`: Stores the actual text content (the document chunk).
        *   `cmetadata`: A JSONB column to store arbitrary metadata associated with the document (e.g., source, title, chunk number).
    *   **Index (`langchain_pg_embedding_embedding_idx`):** This is crucial for fast similarity searches. `HNSW` (Hierarchical Navigable Small World) is a modern and efficient indexing method for vector similarity search. `vector_cosine_ops` specifies that searches will use cosine similarity, common for text embeddings.

## 4. (Optional) Create a Dedicated Database User

While you can use the `postgres` superuser, it's a good security practice to create a dedicated user with specific permissions for your application.

```sql
-- Connect as postgres user to rag_lab_db if not already connected
psql "host=${ADB_INSTANCE_IP} user=${ADB_USER} dbname=${ADB_DATABASE} sslmode=require"

-- Inside psql:
CREATE USER rag_app_user WITH PASSWORD 'YOUR_SECURE_APP_PASSWORD'; -- Replace with a strong password
GRANT CONNECT ON DATABASE rag_lab_db TO rag_app_user;
GRANT USAGE ON SCHEMA public TO rag_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON langchain_pg_collection TO rag_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON langchain_pg_embedding TO rag_app_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO rag_app_user; -- If using serial IDs

-- Exit psql
\q
```
Remember to replace `YOUR_SECURE_APP_PASSWORD` with a strong, unique password. You would then use these credentials in your application's database connection string. For this lab, continuing with the `postgres` user for simplicity is also an option if clearly stated.

Your AlloyDB database is now initialized with the necessary extensions and table structure to support a LangChain-based RAG application. The next steps will involve populating these tables with data and embeddings.
