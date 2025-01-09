from config import Config
from data_processor import DataProcessor
import streamlit as st

class VectorStore:
    def __init__(self, clients):
        self.clients = clients

    def get_embeddings(self, text):
        response = self.clients.openai_client.embeddings.create(
            input=text,
            model=Config.EMBEDDING_MODEL
        )
        return response.data[0].embedding

    def process_and_store_content(self, content, collection, source_type, source_name):
        content_hash = DataProcessor.calculate_sha256(str(content))
        try:
            existing_docs = collection.get(where={"content_hash": content_hash})
            if not existing_docs['ids']:
                for chunk in content:
                    embeddings = self.get_embeddings(chunk["content"])
                    collection.add(
                        embeddings=[embeddings],
                        documents=[chunk["content"]],
                        metadatas=[{
                            "source_type": source_type,
                            "source_name": source_name,
                            "page_number": chunk["page_number"],
                            "content_hash": content_hash
                        }],
                        ids=[f"{content_hash}_chunk_{chunk['page_number']}"]
                    )
                return True
            return False
        except Exception as e:
            st.error(f"Error processing content: {str(e)}")
            return False

    def query_collections(self, query_text, n_results=3):
        query_embedding = self.get_embeddings(query_text)
        try:
            company_results = self.clients.company_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            user_results = self.clients.user_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            context = {
                "COMPANY INFO": [],
                "USER INFO": []
            }
            
            if company_results['documents'][0]:
                context["COMPANY INFO"].extend([
                    f"{company_results['documents'][0][i]}"
                    for i in range(len(company_results['documents'][0]))
                ])
            if user_results['documents'][0]:
                context["USER INFO"].extend([
                    f"{user_results['documents'][0][i]}"
                    for i in range(len(user_results['documents'][0]))
                ])
                
            formatted_context = ""
            if context["COMPANY INFO"]:
                formatted_context += "<< COMPANY INFO >>\n" + "\n".join(context["COMPANY INFO"]) + "\n\n"
            if context["USER INFO"]:
                formatted_context += "<< USER INFO >>\n" + "\n".join(context["USER INFO"])
                
            return formatted_context
        except Exception as e:
            st.error(f"Error querying collections: {str(e)}")
            return ""

    def clear_collections(self):
        try:
            company_ids = self.clients.company_collection.get()['ids']
            user_ids = self.clients.user_collection.get()['ids']
            if company_ids:
                self.clients.company_collection.delete(ids=company_ids)
            if user_ids:
                self.clients.user_collection.delete(ids=user_ids)
            return True
        except Exception as e:
            st.error(f"Error clearing collections: {str(e)}")
            return False