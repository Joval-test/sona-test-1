import pandas as pd
from .leads import generate_email_content, generate_private_link
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_chroma import Chroma
import os
from datetime import datetime

def generate_user_chat_response(uuid, chat_history):
    # Load user info from report.xlsx
    REPORT_PATH = 'data/report.xlsx'
    if not os.path.exists(REPORT_PATH):
        return "Sorry, we couldn't find your information."
    df = pd.read_excel(REPORT_PATH)
    user_row = df[df['ID'].astype(str) == str(uuid)]
    if user_row.empty:
        return "Sorry, we couldn't find your information."
    user_info = {
        'name': user_row.iloc[0]['Name'],
        'company': user_row.iloc[0]['Company'],
        'email': user_row.iloc[0]['Email']
    }
    # Setup LLM and Chroma (reuse your logic)
    azure_endpoint = os.environ.get('AZURE_ENDPOINT', '')
    azure_deployment = os.environ.get('AZURE_DEPLOYMENT', '')
    azure_api_version = os.environ.get('AZURE_API_VERSION', '')
    azure_api_key = os.environ.get('AZURE_API_KEY', '')
    azure_embedding_deployment = os.environ.get('AZURE_EMBEDDING_DEPLOYMENT', '')
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_embedding_deployment,
        openai_api_version=azure_api_version,
        api_key=azure_api_key
    )
    llm = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        api_version=azure_api_version,
        api_key=azure_api_key,
        temperature=0.1
    )
    company_collection = Chroma(
        collection_name="company_info_store",
        persist_directory='data/chroma_store',
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )
    # Compose context from chat_history and company info
    context = "\n".join([f"{msg['role']}: {msg['message']}" for msg in chat_history])
    # Use your LLM logic to generate a response (can be improved for multi-turn)
    # For now, use generate_email_content as a placeholder
    response = generate_email_content(company_collection, user_info, llm, embeddings, product_link=generate_private_link(uuid))
    return response or "Sorry, I couldn't generate a response right now." 