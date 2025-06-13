import pandas as pd
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import HumanMessage
import os
from logging_utils import stage_log
from .chat_manager import ChatManager

def setup_llm_and_embeddings():
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
    
    return llm, embeddings

def setup_company_collection(embeddings):
    return Chroma(
        collection_name="company_info_store",
        persist_directory='data/chroma_store',
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )

def get_user_info(uuid):
    REPORT_PATH = 'data/report.xlsx'
    if not os.path.exists(REPORT_PATH):
        return None
    df = pd.read_excel(REPORT_PATH)
    user_row = df[df['ID'].astype(str) == str(uuid)]
    if user_row.empty:
        return None
    return {
        'name': user_row.iloc[0]['Name'],
        'company': user_row.iloc[0]['Company'],
        'email': user_row.iloc[0]['Email']
    }

def update_report(uuid, chat_history, llm):
    REPORT_PATH = 'data/report.xlsx'
    if not os.path.exists(REPORT_PATH):
        return False
        
    # Generate summary
    messages_content = [f"{msg['role']}: {msg['message']}" for msg in chat_history]
    summary_prompt = f"Summarize this conversation in 50 words, including any contact details and key points discussed: {messages_content}"
    summary_msg = HumanMessage(content=summary_prompt)
    summary = llm.invoke([summary_msg]).content.strip()
    
    # Determine interest status
    status_prompt = f"Based on this conversation {messages_content}, categorize interest as 'Hot' (very interested), 'Warm' (partially interested), or 'Cold' (not interested). Reply with one word only."
    status_msg = HumanMessage(content=status_prompt)
    status = llm.invoke([status_msg]).content.strip()
    
    # Update Excel file
    df = pd.read_excel(REPORT_PATH)
    mask = df['ID'].astype(str) == str(uuid)
    if mask.any():
        df.loc[mask, 'Chat Summary'] = summary
        df.loc[mask, 'Status (Hot/Warm/Cold/Not Responded)'] = status
        df.loc[mask, 'Connected'] = True
        # Add new columns if not present
        if 'Pending Meeting Email' not in df.columns:
            df['Pending Meeting Email'] = ''
        if 'Pending Meeting Info' not in df.columns:
            df['Pending Meeting Info'] = ''
        if 'Meeting Email Sent' not in df.columns:
            df['Meeting Email Sent'] = ''
        # If status is Hot and no pending meeting, auto-generate proposal
        if status == 'Hot' and not df.loc[mask, 'Pending Meeting Email'].iloc[0]:
            try:
                from pkg.backend.app import orchestrate_meeting_flow
            except ImportError:
                from ..app import orchestrate_meeting_flow
            lead_email = df.loc[mask, 'Email'].iloc[0]
            lead_name = df.loc[mask, 'Name'].iloc[0]
            result = orchestrate_meeting_flow(summary, lead_email, lead_name, send_email=False)
            if result.get('success'):
                # Compose email content for review
                product = result.get('product', '')
                responsible = result.get('responsible', {})
                meeting_link = result.get('meeting_link', '')
                slot = result.get('slot', '')
                email_content = f"Hi {lead_name}, your meeting for {product} is scheduled with {responsible.get('name','')} at {slot}. Meeting Link: {meeting_link}"
                df.loc[mask, 'Pending Meeting Email'] = email_content
                import json
                df.loc[mask, 'Pending Meeting Info'] = json.dumps(result)
                df.loc[mask, 'Meeting Email Sent'] = 'No'
        df.to_excel(REPORT_PATH, index=False)
        return True
    return False

def generate_user_chat_response(uuid, chat_history):
    user_info = get_user_info(uuid)
    if not user_info:
        return "Sorry, we couldn't find your information."
    
    llm, embeddings = setup_llm_and_embeddings()
    company_collection = setup_company_collection(embeddings)
    
    chat_manager = ChatManager(llm, embeddings, company_collection)
    messages = chat_manager.convert_to_messages(chat_history, user_info)
    
    response = llm.invoke(messages)
    response_content = response.content
    
    # Check if conversation is ended
    if "have a great day" in response_content.lower():
        # Update report with summary and status
        update_report(uuid, chat_history + [
            {"role": "ai", "message": response_content}
        ], llm)
    
    return response_content