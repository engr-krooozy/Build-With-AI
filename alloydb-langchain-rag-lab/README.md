# Building an LLM and RAG-based Chat Application using AlloyDB AI and LangChain

Welcome to this hands-on codelab where you will learn how to build a complete Retrieval Augmented Generation (RAG) application. This lab will guide you through using AlloyDB for PostgreSQL as a powerful vector database with its AlloyDB AI capabilities, integrating it with LangChain for building the RAG pipeline, and deploying the application components on Google Cloud.

By the end of this codelab, you will have a functional chat application that can answer questions based on a knowledge base stored and queried using AlloyDB AI, with the language understanding and generation powered by Vertex AI models through LangChain.

## What You'll Build

You will construct a RAG system consisting of:

1.  **AlloyDB for PostgreSQL:** Configured with AlloyDB AI (`google_ml_integration` and `vector` extensions) to store text documents and their vector embeddings, enabling efficient similarity searches.
2.  **A GCE VM:** To host development tools, the sample chat application, and scripts for database interaction.
3.  **A RAG Retrieval Service:** A FastAPI application deployed on Cloud Run that uses LangChain to:
    *   Receive user queries.
    *   Generate query embeddings using Vertex AI.
    *   Retrieve relevant documents from AlloyDB using vector search.
    *   Pass the retrieved context and the original query to a Vertex AI LLM to generate a final answer.
4.  **A Sample Chat Application:** A Streamlit application running on the GCE VM, providing a user interface to interact with your RAG service.

![High-level architecture diagram (conceptual)](./assets/conceptual_architecture.png) 
*(Note: You might want to add an actual architecture diagram image to an `assets` folder later)*

## Prerequisites

Before you begin, please ensure you have met all the setup and software requirements detailed in:
*   [01 - Setup and Requirements](./01-setup-requirements.md)

## Codelab Modules

Follow these modules step-by-step to complete the lab:

1.  **[00 - Introduction](./00-introduction.md)**
    *   Overview of the lab, learning objectives, and technologies used.
2.  **[01 - Setup and Requirements](./01-setup-requirements.md)**
    *   Detailed list of necessary Google Cloud setup, accounts, and tools.
3.  **[02 - Before You Begin](./02-before-you-begin.md)**
    *   Initial Google Cloud environment configuration: enabling APIs, setting environment variables.
4.  **[03 - Deploy AlloyDB Cluster](./03-deploy-alloydb-cluster.md)**
    *   Setting up VPC peering, creating an AlloyDB cluster and primary instance.
5.  **[04 - Prepare GCE Virtual Machine](./04-prepare-gce-vm.md)**
    *   Creating and configuring a GCE VM with necessary tools (psql, Python, git).
6.  **[05 - Initialize the Database](./05-initialize-database.md)**
    *   Connecting to AlloyDB, creating a database, enabling `vector` and `google_ml_integration` extensions, and setting up tables for RAG.
7.  **[06 - Deploy the Retrieval Service](./06-deploy-retrieval-service.md)**
    *   Building and deploying the LangChain-based FastAPI RAG service on Cloud Run.
8.  **[07 - Deploy Sample Chat Application](./07-deploy-sample-application.md)**
    *   Running a Streamlit chat application on the GCE VM to interact with the RAG service.
9.  **[08 - Clean Up Environment](./08-cleanup-environment.md)**
    *   Instructions to delete all created Google Cloud resources to avoid further charges.
10. **[09 - Congratulations](./09-congratulations.md)**
    *   Summary of achievements and next steps.

Let's get started! Navigate to [00 - Introduction](./00-introduction.md).
