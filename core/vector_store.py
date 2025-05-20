from langchain_core.documents import Document
from langchain_chroma import Chroma
import streamlit as st
import hashlib
import config
from apps.utils.stage_logger import stage_log

@stage_log(stage=2)
def calculate_sha256(content):
    if isinstance(content, str):
        return hashlib.sha256(content.encode()).hexdigest()
    return hashlib.sha256(content).hexdigest()

@stage_log(stage=2)
def initialize_collections(embeddings):
    return Chroma(
        collection_name="company_info_store",
        persist_directory=config.PERSIST_DIRECTORY,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )

@stage_log(stage=2)
def process_and_store_content(content, collection, source_type, source_name):
    content_hash = calculate_sha256(str(content))
    print("CONTENT HASH:", content_hash)

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
                print(f"Successfully added {len(chunk_documents)} chunks to the vector store.")
                return "success"
        else:
            print("Document already exists in the vector store.")
            return "file_exists"

    except Exception as e:
        print(f"Error adding documents: {e}")

@stage_log(stage=2)
def query_collections(query_text, company_collection, user_info, embeddings, llm, n_results=3):
    try:
        company_results = company_collection.similarity_search_by_vector(
            embedding=embeddings.embed_query(query_text), k=1
        )
        
        context = {
            "COMPANY INFO": [],
            "USER INFO": []
        }
        
        if company_results and len(company_results) > 0:
            for result in company_results:
                if hasattr(result, "page_content"):
                    context["COMPANY INFO"].append(result.page_content)

        formatted_context = ""
        if context["COMPANY INFO"]:
            company_info=context["COMPANY INFO"]
            formatted_context += "<< COMPANY INFO >>\n" + "\n".join(company_info) + "\n\n <<END OF COMPANY INFO>>\n\n"
        if user_info:
            formatted_context += "<< USER INFO >>\n" + "\n".join(user_info) + "\n\n <<END OF USER INFO>>"
        
        return formatted_context
    except Exception as e:
        st.error(f"Error querying collections: {str(e)}")
        return ""

@stage_log(stage=3)
def clear_collections(company_collection):
    try:
        company_ids = company_collection.get()['ids']
        if company_ids:
            company_collection.delete(ids=company_ids)
        return True
    except Exception as e:
        st.error(f"Error clearing collections: {str(e)}")
        return False