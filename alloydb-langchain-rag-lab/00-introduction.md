# Introduction

In this codelab, you will learn how to build a RAG (Retrieval Augmented Generation) based chat application using AlloyDB AI, LangChain, and a custom GenAI Databases Retrieval Service. This application will allow users to interact with a large language model (LLM) that can retrieve information from a database to provide more accurate and contextually relevant responses.

## What you'll learn

* How to deploy an AlloyDB Cluster and configure it for AI workloads.
* How to set up and use AlloyDB AI's capabilities for vector embeddings and similarity search.
* How to integrate LangChain with AlloyDB AI to build a RAG pipeline.
* How to configure and deploy a GenAI Databases Retrieval Service that connects LangChain to your AlloyDB instance.
* How to deploy a sample interactive chat application that uses the deployed RAG system.

## Technologies you'll use

* **AlloyDB AI:** A fully managed, PostgreSQL-compatible database service that provides built-in support for vector embeddings and similarity search, crucial for RAG applications.
* **LangChain:** A framework for developing applications powered by language models. It provides tools and abstractions to easily build complex LLM workflows, including RAG.
* **Retrieval Augmented Generation (RAG):** An AI framework for improving the quality of LLM responses by grounding the model on external sources of knowledge. In this lab, the knowledge base will be stored in AlloyDB.
* **Google Cloud Platform:** Including services like Compute Engine for hosting the application and retrieval service, and Cloud Shell for development.

## Prerequisites

* A basic understanding of the Google Cloud Console.
* Basic skills in command line interface and Google Cloud Shell.
* Familiarity with Python is helpful but not strictly required.
* A Google Cloud Account and Google Cloud Project.
* A web browser such as Chrome.
