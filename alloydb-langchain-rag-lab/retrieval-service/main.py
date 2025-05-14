import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain.chains import RetrievalQA

# Configuration from environment variables
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", 5432)
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "textembedding-gecko@latest")
LANGUAGE_MODEL_NAME = os.environ.get("LANGUAGE_MODEL_NAME", "gemini-pro")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "documents") # Default collection name

# Validate essential configuration
if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise ValueError("Missing one or more essential database environment variables: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")

# AlloyDB Connection String
# Ensure you have the google-cloud-alloydb-connector and pg8000 installed
# The AlloyDB Connector handles secure connection, including IAM authentication if configured.
# For direct IP connection (e.g. within the same VPC with appropriate firewall), you might use a simpler psycopg2 string.
# However, the connector is recommended for robustness and IAM auth.
# For this example, we'll construct a standard PostgreSQL connection string,
# assuming the Cloud Run service will connect via its IP within the VPC or via a VPC connector.
# If using AlloyDB Auth Proxy or Connector with IAM, connection string might differ.
CONNECTION_STRING = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# LangChain components
# Initialize embeddings (using Vertex AI through AlloyDB AI's google_ml_integration or directly)
# For this example, we'll use VertexAIEmbeddings directly.
# If leveraging AlloyDB AI's embedding generation via google_ml_integration,
# you might use a different LangChain embedding class or custom SQL.
embeddings = VertexAIEmbeddings(model_name=EMBEDDING_MODEL_NAME)

# Initialize PGVector vector store
# Assumes tables 'langchain_pg_embedding' and 'langchain_pg_collection' exist as per 05-initialize-database.md
# The collection_name parameter is crucial for multi-tenancy or organizing different document sets.
vector_store = PGVector(
    connection_string=CONNECTION_STRING,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
    # use_jsonb=True, # If your metadata is stored in JSONB
)

# Initialize LLM
llm = ChatVertexAI(model_name=LANGUAGE_MODEL_NAME)

# Initialize FastAPI app
app = FastAPI(
    title="AlloyDB RAG Retrieval Service",
    description="An API service for performing Retrieval Augmented Generation using LangChain, AlloyDB, and Vertex AI.",
)

# --- Basic RAG Chain (Question Answering) ---
# This chain retrieves documents and then uses an LLM to answer a question based on them.
template_qa = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt_qa = ChatPromptTemplate.from_template(template_qa)

retriever = vector_store.as_retriever()

# Simple RetrievalQA chain
# qa_chain = RetrievalQA.from_chain_type(
#     llm=llm,
#     chain_type="stuff", # Options: "stuff", "map_reduce", "refine", "map_rerank"
#     retriever=retriever,
#     return_source_documents=True # Optionally return source documents
# )

# More flexible LCEL RAG chain
rag_chain = (
    RunnablePassthrough.assign(context=(lambda x: x["question"]) | retriever)
    | prompt_qa
    | llm
    | StrOutputParser()
)


# --- API Models ---
class QueryRequest(BaseModel):
    question: str
    collection_name: Optional[str] = COLLECTION_NAME # Allow overriding collection per request

class DocumentResponse(BaseModel):
    page_content: str
    metadata: Optional[dict] = None

class AnswerResponse(BaseModel):
    answer: str
    source_documents: Optional[List[DocumentResponse]] = None

class HealthResponse(BaseModel):
    status: str

# --- API Endpoints ---
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/retrieve", response_model=List[DocumentResponse])
async def retrieve_documents(request: QueryRequest):
    """
    Retrieves relevant documents from the vector store based on the query.
    """
    try:
        # If collection_name is provided in request, use a new VectorStore instance for that collection
        current_vector_store = vector_store
        if request.collection_name and request.collection_name != COLLECTION_NAME:
            current_vector_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=embeddings,
                collection_name=request.collection_name,
            )
        
        retrieved_docs = current_vector_store.similarity_search(request.question, k=5) # Get top 5 docs
        return [
            DocumentResponse(page_content=doc.page_content, metadata=doc.metadata)
            for doc in retrieved_docs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag_answer", response_model=AnswerResponse)
async def get_rag_answer(request: QueryRequest):
    """
    Performs Retrieval Augmented Generation to answer a question.
    Retrieves documents and then uses an LLM to generate an answer.
    """
    try:
        # If collection_name is provided in request, need to re-initialize retriever for that collection
        current_retriever = retriever
        if request.collection_name and request.collection_name != COLLECTION_NAME:
            temp_vector_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=embeddings,
                collection_name=request.collection_name,
            )
            current_retriever = temp_vector_store.as_retriever()

        # Re-build chain if retriever changed
        current_rag_chain = (
            RunnablePassthrough.assign(context=(lambda x: x["question"]) | current_retriever)
            | prompt_qa
            | llm
            | StrOutputParser()
        )
        
        result = current_rag_chain.invoke({"question": request.question})
        
        # To get source documents, we'd need to run retriever separately or adjust the chain
        # For this example, we'll run retriever separately for simplicity if source docs are needed.
        # Note: This is not the most efficient way if the chain could return them directly.
        source_docs_retrieved = current_retriever.get_relevant_documents(request.question)
        
        return AnswerResponse(
            answer=result, 
            source_documents=[
                DocumentResponse(page_content=doc.page_content, metadata=doc.metadata) 
                for doc in source_docs_retrieved
            ]
        )
    except Exception as e:
        print(f"Error in /rag_answer: {e}") # Log error
        raise HTTPException(status_code=500, detail=str(e))

# --- Data Ingestion Endpoint (Example - Use with caution in production) ---
class AddTextRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[dict]] = None
    collection_name: Optional[str] = COLLECTION_NAME

@app.post("/add_texts", status_code=201)
async def add_texts_to_vector_store(request: AddTextRequest):
    """
    Adds new texts and their embeddings to the specified collection in the vector store.
    """
    try:
        current_vector_store = vector_store
        if request.collection_name and request.collection_name != COLLECTION_NAME:
            current_vector_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=embeddings,
                collection_name=request.collection_name,
                # Ensure this collection exists or is created if PGVector supports it
            )

        ids = current_vector_store.add_texts(texts=request.texts, metadatas=request.metadatas)
        return {"message": "Texts added successfully", "ids": ids, "collection_name": request.collection_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
