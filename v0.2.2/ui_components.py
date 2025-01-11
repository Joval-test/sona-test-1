import streamlit as st
import base64
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import tempfile
import config
from data_processor import extract_text_from_pdf, extract_text_from_url
from vector_store import process_and_store_content, clear_collections, query_collections
from prompts import create_system_message

def initialize_session_state():
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
    if 'hide_info_bar' not in st.session_state:
        st.session_state.hide_info_bar = False
    if 'company_collection' not in st.session_state:
        st.session_state.company_collection = None
    if 'user_collection' not in st.session_state:
        st.session_state.user_collection = None

def setup_company_section():
    st.header("Company Information")
    company_source = st.radio("Select company info source:", ["PDF", "URL"], key="company_source")
    
    if company_source == "PDF":
        company_files = st.file_uploader("Upload company information PDFs", type="pdf", accept_multiple_files=True, key="company_files")
        
        if company_files and st.button("Process Company Files", key="process_company_files"):
            process_company_files(company_files)
    
    elif company_source == "URL":
        company_urls = st.text_area("Enter company website URLs (one per line):", key="company_urls")
        if company_urls and st.button("Process Company URLs", key="process_company_urls"):
            process_company_urls(company_urls)

def setup_user_section():
    st.header("User Information")
    user_source = st.radio("Select user info source:", ["PDF", "URL"], key="user_source")
    
    if user_source == "PDF":
        user_files = st.file_uploader("Upload user information PDFs", type="pdf", accept_multiple_files=True, key="user_files")
        
        if user_files and st.button("Process User Files", key="process_user_files"):
            process_user_files(user_files)
    
    elif user_source == "URL":
        user_urls = st.text_area("Enter user profile URLs (one per line):", key="user_urls")
        if user_urls and st.button("Process User URLs", key="process_user_urls"):
            process_user_urls(user_urls)

def setup_sidebar():
    st.sidebar.image(config.LOGO_PATH, width=300)
    
    with st.sidebar.expander("💻 Workspace", expanded=False):
        st.header("This is the workspace")
    
    with st.sidebar.expander("🛠️ Settings", expanded=False):
        setup_company_section()
        setup_user_section()
    
    with st.sidebar.expander("❔Help", expanded=False):
        if st.button("Clear All Data"):
            if clear_collections(st.session_state.company_collection, st.session_state.user_collection):
                clear_session_state()
                st.rerun()
    
    st.sidebar.image(config.CAZE_PATH, use_container_width=True)

def setup_header():
    with open(config.ICON_PATH, "rb") as image_file:
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
    st.markdown(image_and_heading_html, unsafe_allow_html=True)
    st.write("")

def process_company_files(files):
    st.info(f"Processing {len(files)} company file(s)...")
    progress_bar = st.progress(0)
    total_files = len(files)
    
    for idx, file in enumerate(files):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.getvalue())
                temp_file_path = temp_file.name
            
            content = extract_text_from_pdf(temp_file_path)
            result = process_and_store_content(content, st.session_state.company_collection, "pdf", file.name)
            
            handle_processing_result(result, "Company", file.name)
            if result in ["file_exists", "success"]:
                st.session_state.company_files_processed += 1
                
        except Exception as e:
            st.error(f"Error processing company file {file.name}: {e}")
        progress_bar.progress((idx + 1) / total_files)
    st.success("All company files have been processed!")

def process_company_urls(urls):
    for url in urls.split('\n'):
        if url.strip():
            content = extract_text_from_url(url.strip())
            result = process_and_store_content(content, st.session_state.company_collection, "url", url.strip())
            handle_processing_result(result, "Company", url.strip())

def process_user_files(files):
    st.info(f"Processing {len(files)} user file(s)...")
    progress_bar = st.progress(0)
    total_files = len(files)
    
    for idx, file in enumerate(files):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.getvalue())
                temp_file_path = temp_file.name
            
            content = extract_text_from_pdf(temp_file_path)
            result = process_and_store_content(content, st.session_state.user_collection, "pdf", file.name)
            
            handle_processing_result(result, "User", file.name)
            if result in ["file_exists", "success"]:
                st.session_state.user_files_processed += 1
                
        except Exception as e:
            st.error(f"Error processing user file {file.name}: {e}")
        progress_bar.progress((idx + 1) / total_files)
    st.success("All user files have been processed!")

def process_user_urls(urls):
    for url in urls.split('\n'):
        if url.strip():
            content = extract_text_from_url(url.strip())
            result = process_and_store_content(content, st.session_state.user_collection, "url", url.strip())
            handle_processing_result(result, "User", url.strip())

def handle_processing_result(result, source_type, name):
    if result == "file_exists":
        st.warning(f"{source_type} file already exists: {name}")
    elif result == "success":
        st.success(f"Processed {source_type.lower()} file successfully: {name}")
    else:
        st.error(f"Failed to process {source_type.lower()} file: {name}")

def clear_session_state():
    st.session_state.conversation_started = False
    st.session_state.conversation_ended = False
    st.session_state.messages = []
    st.session_state.company_files_processed = 0
    st.session_state.user_files_processed = 0
    st.session_state.show_chat = False

def handle_conversation_start(button_container, llm, embeddings, company_collection, user_collection):
    company_has_docs = len(company_collection.get()['ids']) > 0
    user_has_docs = len(user_collection.get()['ids']) > 0

    if company_has_docs and user_has_docs:
        st.session_state.show_chat = True
        st.session_state.hide_info_bar = True
        button_container.empty()
    else:
        st.error("Please upload and process at least one company file/URL and one user file/URL before starting the conversation.")

def handle_chat_interface(llm, embeddings, company_collection, user_collection):
    if not st.session_state.conversation_started:
        initial_context = query_collections("company information and user information", company_collection, user_collection, embeddings)
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
    
    display_chat_history()
    handle_user_input(llm, embeddings, company_collection, user_collection)

def display_chat_history():
    for message in st.session_state.messages[1:]:
        if isinstance(message, AIMessage):
            st.chat_message("assistant", avatar=config.ICON_PATH).write(message.content)
        elif isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)

def handle_user_input(llm, embeddings, company_collection, user_collection):
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
    else:
        user_input = st.chat_input("Your response:")
        
        if user_input:
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.chat_message("user").write(user_input)
            
            context = query_collections(user_input, company_collection, user_collection, embeddings)
            st.session_state.messages[0] = create_system_message(context)
        
            response = llm(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=response.content))
            st.chat_message("assistant", avatar=config.ICON_PATH).write(response.content)
            
            if "have a great day" in response.content.lower():
                st.session_state.conversation_ended = True
                st.rerun()