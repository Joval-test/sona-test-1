from langchain_core.documents import Document
import streamlit as st
from data_processor import *

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

def query_collections(query_text, company_collection, user_info, embeddings, n_results=3):
    try:
        company_results = company_collection.similarity_search_by_vector(
            embedding=embeddings.embed_query(query_text), k=1
        )
        # user_results = user_collection.similarity_search_by_vector(
        #     embedding=embeddings.embed_query(query_text), k=1
        # )
        
        context = {
            "COMPANY INFO": [],
            "USER INFO": []
        }
        
        if company_results and len(company_results) > 0:
            for result in company_results:
                if hasattr(result, "page_content"):
                    context["COMPANY INFO"].append(result.page_content)

        # if user_results and len(user_results) > 0:
        #     for result in user_results:
        #         if hasattr(result, "page_content"):
        #             context["USER INFO"].append(result.page_content)
        
        # if user_info:
        #     print(user_info)
        formatted_context = ""
        if context["COMPANY INFO"]:
            formatted_context += "<< COMPANY INFO >>\n" + "\n".join(context["COMPANY INFO"]) + "\n\n"
        if user_info:
            formatted_context += "<< USER INFO >>\n" + "\n".join(user_info)
        
        return formatted_context
    except Exception as e:
        st.error(f"Error querying collections: {str(e)}")
        return ""

def clear_collections(company_collection): #add User collection incase we're using vector store
    try:
        company_ids = company_collection.get()['ids']
        # user_ids = user_collection.get()['ids']
        
        if company_ids:
            company_collection.delete(ids=company_ids)
        # if user_ids:
        #     user_collection.delete(ids=user_ids)
            
        return True
    except Exception as e:
        st.error(f"Error clearing collections: {str(e)}")
        return False