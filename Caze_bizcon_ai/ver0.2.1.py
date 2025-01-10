import streamlit as st
import langchain
from openai import OpenAI
from langchain_openai import ChatOpenAI, AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import os
import base64
from langchain_chroma import Chroma
import hashlib
import io
import requests
from bs4 import BeautifulSoup
import tempfile
from langchain_core.documents import Document
from docling_loader import DoclingPDFLoader

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

llm= AzureChatOpenAI(
    azure_endpoint="https://ai-gpu-ps.openai.azure.com/",
    azure_deployment="gpt40-mini-long-context",  
    api_version="2024-05-01-preview",  
    api_key="dc415207c54e4dd8ba8b60cb66374822",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2)

embeddings = AzureOpenAIEmbeddings(
            azure_endpoint="https://ai-gpu-ps.openai.azure.com/",
            azure_deployment="embedding",
            openai_api_version="2024-05-01-preview",
            api_key="dc415207c54e4dd8ba8b60cb66374822")

PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

# chroma_client = Chroma.PersistentClient(path=PERSIST_DIRECTORY)
company_collection = Chroma(
    collection_name="company_info_store",
    persist_directory= PERSIST_DIRECTORY,
    embedding_function=embeddings,
    collection_metadata={"hnsw:space": "cosine"}
)
user_collection = Chroma(
    collection_name="user_info_store",
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings,
    collection_metadata={"hnsw:space": "cosine"}
)

langchain.debug = True

def calculate_sha256(content):
    """Calculate SHA256 hash of content."""
    if isinstance(content, str):
        return hashlib.sha256(content.encode()).hexdigest()
    return hashlib.sha256(content).hexdigest()

def extract_text_from_pdf(pdf_file):
    """Extract text content from PDF."""
    loader = DoclingPDFLoader(pdf_file)
    docs = loader.load_and_split()
    print(docs)
    return docs

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
    

def process_and_store_content(content, collection, source_type, source_name):
    """
    Process and store content in vector database.

    Args:
        content (list of dict): List of document chunks, each containing text and metadata.
        collection: The vector store collection.
        source_type (str): Type of the source (e.g., 'PDF', 'Website').
        source_name (str): Name of the source (e.g., 'file_name.pdf').
    """
    # Generate a unique hash for the content
    content_hash = calculate_sha256(str(content))
    print("CONTENT HASH:", content_hash)

    try:
        # Check if the document already exists
        existing_docs = collection.get(where={"content_hash": content_hash})

        # If no existing documents with the same hash, add them to the vector store
        if not existing_docs['ids']:
            # Process each chunk of the content
            chunk_ids = []
            chunk_documents = []

            for chunk in content:
                # print("CONTENT TYPE:", type(content))
                # print("CONTENT EXAMPLE:", content[:2])
                # print("CHUNK TYPE:", type(chunk))
                # print("CHUNK:", chunk)
                if hasattr(chunk, "page_content"):
                    metadata={
                        "source_type": source_type,
                        "source_name": source_name,
                        "page_number": chunk.metadata.get("page_number", 1),
                        "content_hash": content_hash
                    }
                    doc = Document(
                        page_content=chunk.page_content,  # Text of the chunk
                        metadata=metadata  # Attach metadata
                    )
                    chunk_ids.append(f"{content_hash}_chunk_{chunk.metadata.get('page_number', 1)}")
                    chunk_documents.append(doc)

                # print("Chunk Documents:", chunk_documents)
                # print("Chunk Metadatas:", chunk_metadatas)
                # print("Chunk IDs:", chunk_ids)
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



def query_collections(query_text, n_results=3):
    """Query both collections and combine results."""
    try:
        # Fetch company and user results
        company_results = company_collection.similarity_search_by_vector(
            embedding=embeddings.embed_query(query_text), k=1
        )
        user_results = user_collection.similarity_search_by_vector(
            embedding=embeddings.embed_query(query_text), k=1
        )
        
        # Initialize context
        context = {
            "COMPANY INFO": [],
            "USER INFO": []
        }
        
        # Process company results
        if company_results and len(company_results) > 0:
            for result in company_results:
                if hasattr(result, "page_content"):
                    context["COMPANY INFO"].append(result.page_content)

        # Process user results
        if user_results and len(user_results) > 0:
            for result in user_results:
                if hasattr(result, "page_content"):
                    context["USER INFO"].append(result.page_content)
        
        # Format the context string
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
- If no name is found, use the above greeting without the name parameter to make it generic and use the company name provided in the

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

current_directory=os.getcwd()
logo_path=os.path.join(current_directory,"images","logo_transparent.png")
caze_path=os.path.join(current_directory,"images","caze_logo_white_trans.png")
icon_path=os.path.join(current_directory,"images","icon.png")

st.sidebar.image(logo_path, width=300)

# Initialize session state variables
if "company_files_processed" not in st.session_state:
    st.session_state.company_files_processed = 0

if "user_files_processed" not in st.session_state:
    st.session_state.user_files_processed = 0
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False
if "hide_info_bar" not in st.session_state:
    st.session_state.hide_info_bar = False

if not st.session_state.hide_info_bar:
    st.info("👈 Let's start by uploading the informations of the company and the user.")


# # Create two columns
# col1, col2 = st.columns([0.2, 0.9])

# # Add the icon in the first column
# with col1:
#     st.image(icon_path, width=400)  # Adjust the width to fit your design

# # Add the title in the second column
# with col2:
#     st.title("Caze BizConAI")

with open(icon_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

st.write("")
st.write("")
st.write("")
image_and_heading_html = f"""
<div style="display: flex; justify-content:center;">
    <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
    <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
            Caze <span style="color: #304654;">BizConAI</span>
</div>
"""
st.markdown(image_and_heading_html,unsafe_allow_html=True)
st.write("")

# Initialize session state variables
if "company_files_processed" not in st.session_state:
    st.session_state.company_files_processed = 0
if "user_files_processed" not in st.session_state:
    st.session_state.user_files_processed = 0
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False
if "hide_info_bar" not in st.session_state:
    st.session_state.hide_info_bar = False

with st.sidebar.expander("💻 Workspace",expanded=False):
    st.header("This is the workspace")

# Sidebar for Input Data
with st.sidebar.expander("🛠️ Settings",expanded=False):
    # Company Information Section
    st.header("Company Information")
    company_source = st.radio("Select company info source:", ["PDF", "URL"], key="company_source")
    
    if company_source == "PDF":
        company_files = st.file_uploader("Upload company information PDFs", type="pdf", accept_multiple_files=True, key="company_files")
        
        if company_files and st.button("Process Company Files", key="process_company_files"):
            st.info(f"Processing {len(company_files)} company file(s)...")  # Inform the user about the upload
            
            # Initialize a progress bar
            company_progress_bar = st.progress(0)
            total_company_files = len(company_files)
            
            for idx, file in enumerate(company_files):
                try:
                    # Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(file.getvalue())
                        temp_file_path = temp_file.name
                    
                    # Extract content from the PDF
                    content = extract_text_from_pdf(temp_file_path)
                    
                    # Process and store the content
                    result = process_and_store_content(content, company_collection, "pdf", file.name)
                    
                    if result == "file_exists":
                        st.warning(f"Company file already exists: {file.name}")
                        st.session_state.company_files_processed += 1
                    elif result == "success":
                        st.success(f"Processed company file successfully: {file.name}")
                        st.session_state.company_files_processed += 1
                    else:
                        st.error(f"Failed to process company file: {file.name}")
                    
                except Exception as e:
                    st.error(f"Error processing company file {file.name}: {e}")
                company_progress_bar.progress((idx + 1) / total_company_files)
            st.success("All company files have been processed!")

    elif company_source == "URL":
        company_urls = st.text_area("Enter company website URLs (one per line):", key="company_urls")
        if company_urls and st.button("Process Company URLs", key="process_company_urls"):
            urls = company_urls.split('\n')
            for url in urls:
                if url.strip():
                    content = extract_text_from_url(url.strip())
                    result = process_and_store_content(content, company_collection, "url", url.strip())
                    if result == "file_exists":
                        st.warning(f"Company URL already exists: {url.strip()}")
                    elif result == "success":
                        st.success(f"Processed company URL successfully: {url.strip()}")
                    else:
                        st.error(f"Failed to process company URL: {url.strip()}")

    st.header("User Information")
    user_source = st.radio("Select user info source:", ["PDF", "URL"], key="user_source")
    
    if user_source == "PDF":
        user_files = st.file_uploader("Upload user information PDFs", type="pdf", accept_multiple_files=True, key="user_files")
        
        if user_files and st.button("Process User Files", key="process_user_files"):
            st.info(f"Processing {len(user_files)} user file(s)...")  # Inform the user about the upload
            
            # Initialize a progress bar
            user_progress_bar = st.progress(0)
            total_user_files = len(user_files)
            
            for idx, file in enumerate(user_files):
                try:
                    # Save the uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        temp_file.write(file.getvalue())
                        temp_file_path = temp_file.name
                    
                    # Extract content from the PDF
                    content = extract_text_from_pdf(temp_file_path)
                    
                    # Process and store the content
                    result = process_and_store_content(content, user_collection, "pdf", file.name)
                    
                    if result == "file_exists":
                        st.warning(f"User file already exists: {file.name}")
                        st.session_state.user_files_processed += 1
                    elif result == "success":
                        st.success(f"Processed user file successfully: {file.name}")
                        st.session_state.user_files_processed += 1
                    else:
                        st.error(f"Failed to process user file: {file.name}")
                    
                except Exception as e:
                    st.error(f"Error processing user file {file.name}: {e}")
                
                # Update the progress bar
                user_progress_bar.progress((idx + 1) / total_user_files)
            
            # Completion message
            st.success("All user files have been processed!")

    elif user_source == "URL":
        user_urls = st.text_area("Enter user profile URLs (one per line):", key="user_urls")
        if user_urls and st.button("Process User URLs", key="process_user_urls"):
            urls = user_urls.split('\n')
            for url in urls:
                if url.strip():
                    content = extract_text_from_url(url.strip())
                    result = process_and_store_content(content, user_collection, "url", url.strip())
                    if result == "file_exists":
                        st.warning(f"User URL already exists: {url.strip()}")
                    elif result == "success":
                        st.success(f"Processed user URL successfully: {url.strip()}")
                    else:
                        st.error(f"Failed to process user URL: {url.strip()}")
                        
with st.sidebar.expander("❔Help",expanded=False):
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

st.sidebar.image(caze_path, use_container_width=True)
# Start Conversation button
button_container = st.empty()

if button_container.button('Start Conversation'):
    if st.session_state.get("company_files_processed", 0) > 0 and st.session_state.get("user_files_processed", 0) > 0:
        st.session_state.show_chat = True
        st.session_state.hide_info_bar=True
        button_container.empty()
    else:
        st.error("Please upload and process at least one company file/URL and one user file/URL before starting the conversation.")

if st.session_state.show_chat:
    if not st.session_state.conversation_started:
        
        initial_context = query_collections("company information and user information", n_results=5)
        if initial_context:
            system_message = create_system_message(initial_context)
            initial_messages = [system_message]
            st.session_state.conversation_started = True

            response = llm(initial_messages)
            st.session_state.messages = initial_messages + [AIMessage(content=response.content)]
            st.session_state.conversation_started = True
        else:
            st.error("No context found. Please ensure company and user information has been properly processed.")
            st.session_state.show_chat = False
      
    # Display chat history
    for message in st.session_state.messages[1:]:
        if isinstance(message, AIMessage):
            st.chat_message("assistant", avatar=icon_path).write(message.content)
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