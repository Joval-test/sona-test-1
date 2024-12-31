import streamlit as st
import langchain
from openai import OpenAI
from langchain_openai import ChatOpenAI
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
# openai.api_key = constants.AZUREKEY
# os.environ["AZURE_OPENAI_API_KEY"] = constants.AZUREKEY
# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://costproject.openai.azure.com/"
# os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "DeploymentCostSense-1"
# os.environ["AZURE_OPENAI_API_VERSION"] = "2023-03-15-preview"

# Initialize OpenAI client for embeddings
openai_client = OpenAI(api_key=constants.APIKEY2)

# # Initialize LLM
# llm = AzureChatOpenAI(
#     azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#     azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
#     openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
# )

# Initialize LLM using LangChain's OpenAI wrapper
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",  # or another appropriate model
    api_key=constants.APIKEY2,
    temperature=0.2
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

langchain.debug = True

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
        
        print("\n\n<<URL PARSED TEXT>>\n\n"+text)
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
        
        # Format results with clear section headers
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
            
        # Format the context string with clear section markers
        formatted_context = ""
        if context["COMPANY INFO"]:
            formatted_context += "<< COMPANY INFO >>\n" + "\n".join(context["COMPANY INFO"]) + "\n\n"
        if context["USER INFO"]:
            formatted_context += "<< USER INFO >>\n" + "\n".join(context["USER INFO"])
            
        return formatted_context
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
    
# Update the system message creation
def create_system_message(context):
    base_instruction = """You are an AI cold calling/texting assistant. Here is the context for our interaction:

{context}

When generating the first message, use the user information provided above to personalize your introduction. If you can't find a name, use a generic greeting.
    """
    
    return SystemMessage(content=base_instruction.format(context=context) + context_instr)

context_instr = '''
<< YOUR TASK >>
You are an AI assistant designed to contact potential business prospects via chat or phone. Your purpose is to identify if the prospect is experiencing specific problems we solve, showcase the value of our solutions, and guide them toward validating and closing the interaction (e.g., scheduling a meeting or exchanging contact details). Follow these guidelines:

1. First Message Format:
- Use the user information to personalize your greeting
- Format: "Hi [name]! I'm an AI assistant from [company]. Do you have a few minutes to chat?"
- If no name is found, use the above greeting without the name parameter to make it generic

2. Identify if the prospect is experiencing known problems:
 Utilise data in << USER INFO >> to infer which one of the company's solutions would be most relevant to the user.
Examples for doing this naturally:
“I saw (something the user is doing/working on/position of user), which led me to believe you're trying to (whatever problem you solve). Are you?”
“I saw that you were running Google ads for laser tattoo removal. That led me to believe you might be looking to bring in more patients. Is that a priority for you right now?”
“Many small business owners spend a few hours every week using tools like PayPal, Stripe, and spreadsheets to manually do their bookkeeping. I'm curious. How are you handling bookkeeping at ABC Company?”

If there is nothing in << USER INFO >> that would give you a hint as to which solution of the company would be relevant to the user, identify this at the earliest.
Present the top 3 common problems we solve.
General example to do this:
“Most (roles) that I talk to tell me that they’re trying to do one of three things: (problem 1), (problem 2), or (problem 3). Does that sound like you at all?”
Specific example:
“Most of the doctors I talk to tell me they are looking to either bring in a higher volume of patients, bring in patients for specific services, or just see more patients who pay out of pocket. Which of those is most important to you?”

3. Show Our Value:
- Only discuss solutions mentioned in << COMPANY INFO >>
- Explain how our solution addresses the identified specific challenge
- Use clear, concise language

4. Validate and Close:
Confirm if the prospect cares about the problems we solve.
If yes, set up a meeting and exchange contact details. After this, refer the guidelines for "End of Conversation".
If no, refer the guidelines for "End of Conversation". 

5. End of Conversation:
When you reach the end of the conversation, you must first ask the user if there's anything else they would like to ask about or if there \
is anything else you can help with. If the user replies in the negative, only then do you end the conversation. \
When you are ending the conversation, always end with "Have a great day!". Do not use this phrase anywhere else except in the final message that is meant to end the chat.

Constraints:
- Keep responses under 20 lines
- Be professional but friendly
- Use first names after initial introduction
- Only discuss features/solutions mentioned in the company information
- If asked about unknown features/solutions, direct to company contact. If you do not have the company's contact information, simply tell the user to get in touch with the company for further details.
- Do not generate the user's response for them. Generate ONLY the AI response message.
'''

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
        initial_context = query_collections("company information and user information", n_results=5)
        if initial_context:
            system_message = create_system_message(initial_context)
            initial_messages = [system_message]
            
            # Get initial response
            response = llm(initial_messages)
            st.session_state.messages = initial_messages + [AIMessage(content=response.content)]
            st.session_state.conversation_started = True
        else:
            st.error("No context found. Please ensure company and user information has been properly processed.")
            st.session_state.show_chat = False
            
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