import streamlit as st
import openai
from openai import OpenAI, AzureOpenAI
from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import os
import constants
import chromadb
import hashlib
import PyPDF2
import io
import requests
from bs4 import BeautifulSoup
import tempfile

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False
if 'conversation_ended' not in st.session_state:
    st.session_state.conversation_ended = False
if 'company_info' not in st.session_state:
    st.session_state.company_info = ""
if 'user_info' not in st.session_state:
    st.session_state.user_info = ""
if 'company_files_processed' not in st.session_state:
    st.session_state.company_files_processed = 0
if 'user_files_processed' not in st.session_state:
    st.session_state.user_files_processed = 0
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

# Configure Azure OpenAI
openai.api_key = constants.AZUREKEY
os.environ["AZURE_OPENAI_API_KEY"] = constants.AZUREKEY
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://costproject.openai.azure.com/"
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "DeploymentCostSense-1"
os.environ["AZURE_OPENAI_API_VERSION"] = "2023-03-15-preview"

# Initialize OpenAI client for embeddings
openai_client = OpenAI(api_key=constants.APIKEY2)

# Initialize LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

# Initialize ChromaDB
PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
company_collection = chroma_client.get_or_create_collection(
    name="company_info_store",
    metadata={"hnsw:space": "cosine"}
)
user_collection = chroma_client.get_or_create_collection(
    name="user_info_store",
    metadata={"hnsw:space": "cosine"}
)

def calculate_sha256(content):
    """Calculate SHA256 hash of content."""
    if isinstance(content, str):
        return hashlib.sha256(content.encode()).hexdigest()
    return hashlib.sha256(content).hexdigest()

def extract_text_from_pdf(pdf_file):
    """Extract text content from PDF."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text_content = []
    
    for page_num in range(len(pdf_reader.pages)):
        text = pdf_reader.pages[page_num].extract_text()
        text_content.append({
            "content": text,
            "page_number": page_num + 1
        })
    
    return text_content

def extract_text_from_url(url):
    """Extract text content from webpage."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return [{"content": text, "page_number": 1}]
    except Exception as e:
        st.error(f"Error extracting text from URL: {str(e)}")
        return []

def get_embeddings(text):
    """Get embeddings using OpenAI API."""
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def process_and_store_content(content, collection, source_type, source_name):
    """Process and store content in vector database."""
    content_hash = calculate_sha256(str(content))
    
    try:
        existing_docs = collection.get(
            where={"content_hash": content_hash}
        )
        
        if not existing_docs['ids']:
            for chunk in content:
                embeddings = get_embeddings(chunk["content"])
                
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

def query_collections(query_text, n_results=3):
    """Query both collections and combine results."""
    query_embedding = get_embeddings(query_text)
    
    try:
        company_results = company_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        user_results = user_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Combine and format results
        context = []
        if company_results['documents'][0]:
            context.extend([
                f"Company Info (from {company_results['metadatas'][0][i]['source_name']}):\n"
                f"{company_results['documents'][0][i]}"
                for i in range(len(company_results['documents'][0]))
            ])
        if user_results['documents'][0]:
            context.extend([
                f"User Info (from {user_results['metadatas'][0][i]['source_name']}):\n"
                f"{user_results['documents'][0][i]}"
                for i in range(len(user_results['documents'][0]))
            ])
            
        return "\n\n".join(context)
    except Exception as e:
        st.error(f"Error querying collections: {str(e)}")
        return ""

def clear_collections():
    """Clear all data from collections."""
    try:
        company_ids = company_collection.get()['ids']
        user_ids = user_collection.get()['ids']
        
        if company_ids:
            company_collection.delete(ids=company_ids)
        if user_ids:
            user_collection.delete(ids=user_ids)
            
        return True
    except Exception as e:
        st.error(f"Error clearing collections: {str(e)}")
        return False

context_instr = '''You are an AI assistant designed to contact potential business prospects via chat or phone. Your purpose is to identify if the prospect is experiencing specific problems we solve, showcase the value of our solutions, and guide them toward validating and closing the interaction (e.g., scheduling a meeting or exchanging contact details). Follow these guidelines:

Introduce the Problem We Solve:
You must start the conversation. Do not start with something open ended like "Hi! How may I help you?" Start with a clear introduction statement like "Hi [full name]! I'm an AI assistant contacting you on behalf of [insert company name]. Do you \
have a few minutes to talk?"
Open with a creative and clear introduction.
Identify if the prospect is experiencing known problems. Utilise data in << USER INFO >> to infer which one of the solutions would be most relevant to the user.
If yes, confirm and proceed.
If no, ask about their top 3 challenges relevant to our solutions
Show Our Value:
Clearly explain why the identified problem exists.
Highlight how we can help solve it.

Validate and Close:
Confirm if the prospect cares about the problems we solve.
If yes, set up a meeting and exchange contact details.
If no, politely close the interaction.
Constraints: Only respond based on the data provided to you about the company, its solutions, and the problems it addresses under << COMPANY INFO >>. Be persuasive but professional, keeping the tone friendly and respectful. Only generate the AI response. \
Do not generate the user's response for them.
When scheduling a meeting, ask for the user's contact information (email/phone) only if you do not already have it.
When you are ending the conversation, always end with "Have a great day!". Do not use this phrase anywhere else except in the final message that is meant to end the chat.
After the initial introduction, refer to the user only by their first name.
Do not speak about any solutions you do not have data about. If asked about a solution or a feature of a solution you do not know about, say that you do not have data about the same and give the user \
    contact information to get in touch with the company to inquire further.
Generate ONLY the AI response message.'''

# Streamlit UI
st.title("AI Sales Assistant")

# Sidebar for data input
with st.sidebar:
    st.header("Input Data")
    
    # Company Information
    st.subheader("Company Information")
    company_source = st.radio("Select company info source:", ["PDF", "URL"], key="company_source")
    
    if company_source == "PDF":
        company_files = st.file_uploader("Upload company information PDFs", type="pdf", accept_multiple_files=True, key="company_files")
        if company_files:
            for file in company_files:
                content = extract_text_from_pdf(io.BytesIO(file.getvalue()))
                if process_and_store_content(content, company_collection, "pdf", file.name):
                    st.session_state.company_files_processed += 1
                    st.success(f"Processed: {file.name}")
    else:
        company_urls = st.text_area("Enter company website URLs (one per line):", key="company_urls")
        if company_urls and st.button("Process Company URLs"):
            urls = company_urls.split('\n')
            for url in urls:
                if url.strip():
                    content = extract_text_from_url(url.strip())
                    if process_and_store_content(content, company_collection, "url", url.strip()):
                        st.session_state.company_files_processed += 1
                        st.success(f"Processed: {url.strip()}")
    
    # User Information
    st.subheader("User Information")
    user_source = st.radio("Select user info source:", ["PDF", "URL"], key="user_source")
    
    if user_source == "PDF":
        user_files = st.file_uploader("Upload user information PDFs", type="pdf", accept_multiple_files=True, key="user_files")
        if user_files:
            for file in user_files:
                content = extract_text_from_pdf(io.BytesIO(file.getvalue()))
                if process_and_store_content(content, user_collection, "pdf", file.name):
                    st.session_state.user_files_processed += 1
                    st.success(f"Processed: {file.name}")
    else:
        user_urls = st.text_area("Enter user profile URLs (one per line):", key="user_urls")
        if user_urls and st.button("Process User URLs"):
            urls = user_urls.split('\n')
            for url in urls:
                if url.strip():
                    content = extract_text_from_url(url.strip())
                    if process_and_store_content(content, user_collection, "url", url.strip()):
                        st.session_state.user_files_processed += 1
                        st.success(f"Processed: {url.strip()}")
    
    if st.button("Clear All Data"):
        if clear_collections():
            st.success("All data cleared")
            st.session_state.conversation_started = False
            st.session_state.conversation_ended = False
            st.session_state.messages = []
            st.session_state.company_files_processed = 0
            st.session_state.user_files_processed = 0
            st.session_state.show_chat = False
            st.rerun()

# Start Conversation button
if st.button("Start Conversation"):
    if st.session_state.company_files_processed > 0 and st.session_state.user_files_processed > 0:
        st.session_state.show_chat = True
    else:
        st.error("Please upload and process at least one company file/URL and one user file/URL before starting the conversation.")

# Main chat interface
if st.session_state.show_chat:
    if not st.session_state.conversation_started:
        initial_context = query_collections("general information")
        if initial_context:
            initial_messages = [
                SystemMessage(content=f"""You are an AI sales assistant. Use the following context for your interactions:

{initial_context}

""" + context_instr)
            ]
            
            response = llm(initial_messages)
            st.session_state.messages = initial_messages + [AIMessage(content=response.content)]
            st.session_state.conversation_started = True
            
    # Display chat history

    for message in st.session_state.messages[1:]:
        if isinstance(message, AIMessage):
            st.chat_message("assistant").write(message.content)
        elif isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)

    # Handle user input
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
    else:
        user_input = st.chat_input("Your response:")
        
        if user_input:
            # Add user message
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.chat_message("user").write(user_input)
            
            # Get relevant context
            context = query_collections(user_input)
            
            # Update system message with new context
            st.session_state.messages[0] = SystemMessage(content=f"""You are an AI sales assistant. Use the following context for your interactions:

{context}

""" + context_instr)
        
            # Get AI response
            response = llm(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=response.content))
            st.chat_message("assistant").write(response.content)
            
        # Check for conversation end
        if "have a great day" in response.content.lower():
            st.session_state.conversation_ended = True
            st.rerun()