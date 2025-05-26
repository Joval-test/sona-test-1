from langchain_core.documents import Document
from langchain_chroma import Chroma
import os
from langchain_openai import AzureOpenAIEmbeddings

PERSIST_DIRECTORY = 'data/chroma_store'

class FallbackEmbeddings:
    def embed_query(self, text):
        return [0.0] * 384
    def embed_documents(self, texts):
        return [[0.0] * 384 for _ in texts]

def get_azure_embeddings():
    endpoint = os.environ.get('AZURE_ENDPOINT', '')
    deployment = os.environ.get('AZURE_EMBEDDING_DEPLOYMENT', '')
    api_version = os.environ.get('AZURE_API_VERSION', '')
    api_key = os.environ.get('AZURE_API_KEY', '')
    if endpoint and deployment and api_version and api_key:
        return AzureOpenAIEmbeddings(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            openai_api_version=api_version,
            api_key=api_key
        )
    else:
        return FallbackEmbeddings()

def get_company_collection():
    embeddings = get_azure_embeddings()
    return Chroma(
        collection_name="company_info_store",
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )

def process_and_store_content(content, collection, source_type, source_name):
    import hashlib
    content_hash = hashlib.sha256(str(content).encode()).hexdigest()
    try:
        existing_docs = collection.get(where={"content_hash": content_hash})
        if not existing_docs['ids']:
            chunk_ids = []
            chunk_documents = []
            for chunk in content:
                if hasattr(chunk, "page_content"):
                    metadata={
                        "source_type": source_type,
                        "source_name": source_name,
                        "page_number": chunk.metadata.get("page_number", 1),
                        "content_hash": content_hash
                    }
                    doc = Document(
                        page_content=chunk.page_content,
                        metadata=metadata
                    )
                    chunk_ids.append(f"{content_hash}_chunk_{chunk.metadata.get('page_number', 1)}")
                    chunk_documents.append(doc)
            collection.add_documents(
                documents=chunk_documents,
                ids=chunk_ids
            )
            return "success"
        else:
            return "file_exists"
    except Exception as e:
        return f"error: {str(e)}"

def clear_company_collection():
    collection = get_company_collection()
    try:
        company_ids = collection.get()['ids']
        if company_ids:
            collection.delete(ids=company_ids)
        return True
    except Exception:
        return False 