import streamlit as st
import openai
from openai import OpenAI
from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from langchain.embeddings import AzureOpenAIEmbeddings
import os
import constants
import chromadb
import hashlib
import PyPDF2
import io

# Initialize session state to store conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False

if 'conversation_ended' not in st.session_state:
    st.session_state.conversation_ended = False

# Configure Azure OpenAI
openai.api_key = constants.AZUREKEY
os.environ["AZURE_OPENAI_API_KEY"] = constants.AZUREKEY
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://costproject.openai.azure.com/"
os.environ["AZURE_OPENAI_GPT4_DEPLOYMENT"] = ''
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "DeploymentCostSense-1"
os.environ["AZURE_OPENAI_API_VERSION"] = "2023-03-15-preview"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = constants.LANGCHAIN_KEY

# Initialize LLM
llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

openai_client = OpenAI(api_key=constants.APIKEY2)

PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
collection = chroma_client.get_or_create_collection(
    name="document_store",
    metadata={"hnsw:space": "cosine"}
)

# --- FUNCTIONS ---
def calculate_sha256(file_content):
    """Calculate SHA256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()

def extract_text_from_pdf(pdf_file):
    """Extract text content from PDF using PyPDF2."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text_content = []
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        text_content.append({
            "content": text,
            "page_number": page_num + 1
        })
    
    return text_content

def process_pdf(uploaded_file):
    text_content = extract_text_from_pdf(io.BytesIO(uploaded_file.getvalue()))    
    return text_content

def get_embeddings(text):
    response = openai_client.embeddings.create(
        input=text,
        # model="text-embedding-3-small"
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def get_stored_files():
    """Get list of unique files stored in the database."""
    try:
        all_metadata = collection.get()['metadatas']
        if all_metadata:
            # Create a dictionary to store unique files and their hashes
            unique_files = {}
            for metadata in all_metadata:
                unique_files[metadata['file_name']] = metadata['file_hash']
            return unique_files
        return {}
    except Exception as e:
        st.error(f"Error retrieving stored files: {str(e)}")
        return {}
    
def delete_file_vectors(file_hash):
    """Delete all vectors associated with a specific file."""
    try:
        collection.delete(
            where={"file_hash": file_hash}
        )
        return True
    except Exception as e:
        st.error(f"Error deleting file vectors: {str(e)}")
        return False    
    
def clear_all_vectors():
    """Clear all vectors from the database."""
    try:
        all_ids = collection.get()['ids']
        if all_ids:
            collection.delete(ids=all_ids)
        return True
    except Exception as e:
        st.error(f"Error clearing vectors: {str(e)}")
        return False

def process_and_store_documents(uploaded_files):
    """Process uploaded documents and store in ChromaDB."""
    for uploaded_file in uploaded_files:
        file_hash = calculate_sha256(uploaded_file.getvalue())
        try:
            existing_docs = collection.get(
                where={"file_hash": file_hash}
            )
        except Exception as e:
            st.error(f"Error checking document existence: {str(e)}")
            existing_docs = {"ids": []}
        
        if not existing_docs['ids']:
            try:
                structured_content = process_pdf(uploaded_file)
                for page_content in structured_content:
                    embeddings = get_embeddings(page_content["content"])
                    
                    collection.add(
                        embeddings=[embeddings],
                        documents=[page_content["content"]],
                        metadatas=[{
                            "file_name": uploaded_file.name,
                            "page_number": page_content["page_number"],
                            "file_hash": file_hash
                        }],
                        ids=[f"{file_hash}_page_{page_content['page_number']}"]
                    )
                
                st.success(f"Successfully processed and stored {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error processing document {uploaded_file.name}: {str(e)}")
        else:
            st.info(f"Document {uploaded_file.name} already exists in the database")


def query_documents(query_text, n_results=5):  
    """Query the document store and return relevant results."""
    query_embedding = get_embeddings(query_text)
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    except Exception as e:
        st.error(f"Error querying documents: {str(e)}")
        return None
    
def generate_response(query, context, detail_level='normal'):
    """Generate response using OpenAI API with controlled detail level."""
    
    detail_prompts = {
        'brief': "Provide a concise answer based on the context.",
        'normal': "Provide a comprehensive answer based on the context, including key details and examples when available.",
        'detailed': """Provide an extremely detailed answer based on the context. Include:
        1. All relevant facts and figures
        2. Specific examples and references
        3. Direct quotes when applicable
        4. Clear citations to specific pages
        5. Related information from different parts of the context
        6. Explanations of any technical terms
        Please organize the information in a structured way."""
    }

    prompt = f"""You are an AI assistant designed to contact potential business prospects via chat or phone. Your purpose is to identify if the prospect is experiencing specific problems we solve, showcase the value of our solutions, and guide them toward validating and closing the interaction (e.g., scheduling a meeting or exchanging contact details). Follow these guidelines:

Introduce the Problem We Solve:
You must start the conversation. Do not start with something open ended like "Hi! How may I help you?" Start with a clear introduction statement like "Hi [full name]! I'm an AI assistant contacting you on behalf of {insert company name}. Do you \
have a few minutes to talk?"
Open with a creative and clear introduction.
Identify if the prospect is experiencing known problems. Utilise data in << USER INFO >> to infer which one of the solutions would be most relevant to the user.
If yes, confirm and proceed.
If no, ask about their top 3 challenges relevant to our solutions.

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

    Context: {context}

    Question: {query}

    Answer:"""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides detailed analysis based strictly on the provided context. Always cite specific pages and documents when providing information."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=2000 
    )
    
    return response.choices[0].message.content

# Define company and user information


company_info = '''Caze Labs is a startup in Bangalore, India and it focuses on 
innovative products, solutions and services majorly in the areas of 
Cloud, Kubernetes, Artificial Intelligence, Cyber Security, Data 
Management and Open Source.
Products:
Data Sense: Local Assistant for your scattered data 
AI driven custom data assistants for faster inference and data automation. Locally hosted (no internet) copilots which can run on CPU/GPUs
You own your data!
Own your AI Models
Host anywhere!
Support CPU and GPU
Optimized RAG
Agentic Automation
Multisource
Multiformat
Pluggable LLM/Embeddings

Cost Sense: AI-Driven Cost Observability and Management
Unified AI driven cost insights, analysis, savings,  prediction, and optimization for your infrastructure resources and more!
Cost Insights & Savings
Anomaly & Trend
Cost Prediction
Cost Copilot
Custom Cost Groups
Budget planning
Reporting and Alerts
Hybrid Cloud & DCs
Kubernetes and VMs

Contact Details to Give To Prospective Leads:
Email: info@examplecaze.com
Phone: 9090999090
'''

user_info = '''Name: Sanil Kumar
Position: CEO, Caze Labs
'''

# Streamlit UI
st.title("AI Sales Assistant")
st.write("Chat with our AI sales representative")

# Initialize chat if not started
if not st.session_state.conversation_started:
    initial_messages = [
        SystemMessage(content="<< INSTRUCTIONS >>\n"+instructions+"<< COMPANY INFO >>\n"+company_info+"<< USER INFO >>\n"+user_info),
    ]
    response = llm(initial_messages)
    st.session_state.messages = initial_messages + [AIMessage(content=response.content)]
    st.session_state.conversation_started = True

# Display chat history
for message in st.session_state.messages[1:]:  # Skip the system message
    if isinstance(message, AIMessage):
        st.chat_message("assistant").write(message.content)
    elif isinstance(message, HumanMessage):
        st.chat_message("user").write(message.content)

# Check if conversation has ended
if st.session_state.conversation_ended:
    st.write("Conversation has ended. Please refresh the page to start a new conversation.")
else:
    # User input
    user_input = st.chat_input("Your response:")
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.chat_message("user").write(user_input)
        
        # Get AI response
        response = llm(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))
        st.chat_message("assistant").write(response.content)
        
        # Check if conversation should end
        if "have a great day" in response.content.lower():
            st.session_state.conversation_ended = True
            st.rerun()

