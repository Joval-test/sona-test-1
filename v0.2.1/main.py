import streamlit as st
from clients import Clients
from vector_store import VectorStore
from data_processor import DataProcessor
from prompts import Prompts
from langchain.schema import HumanMessage, AIMessage
import io

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

def main():
    initialize_session_state()
    clients = Clients()
    vector_store = VectorStore(clients)
    
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
                    content = DataProcessor.extract_text_from_pdf(io.BytesIO(file.getvalue()))
                    if vector_store.process_and_store_content(content, clients.company_collection, "pdf", file.name):
                        st.session_state.company_files_processed += 1
                        st.success(f"Processed: {file.name}")
        else:
            company_urls = st.text_area("Enter company website URLs (one per line):", key="company_urls")
            if company_urls and st.button("Process Company URLs"):
                urls = company_urls.split('\n')
                for url in urls:
                    if url.strip():
                        content = DataProcessor.extract_text_from_url(url.strip())
                        if vector_store.process_and_store_content(content, clients.company_collection, "url", url.strip()):
                            st.session_state.company_files_processed += 1
                            st.success(f"Processed: {url.strip()}")
        
        # User Information
        st.subheader("User Information")
        user_source = st.radio("Select user info source:", ["PDF", "URL"], key="user_source")
        
        if user_source == "PDF":
            user_files = st.file_uploader("Upload user information PDFs", type="pdf", accept_multiple_files=True, key="user_files")
            if user_files:
                for file in user_files:
                    content = DataProcessor.extract_text_from_pdf(io.BytesIO(file.getvalue()))
                    if vector_store.process_and_store_content(content, clients.user_collection, "pdf", file.name):
                        st.session_state.user_files_processed += 1
                        st.success(f"Processed: {file.name}")
        else:
            user_urls = st.text_area("Enter user profile URLs (one per line):", key="user_urls")
            if user_urls and st.button("Process User URLs"):
                urls = user_urls.split('\n')
                for url in urls:
                    if url.strip():
                        content = DataProcessor.extract_text_from_url(url.strip())
                        if vector_store.process_and_store_content(content, clients.user_collection, "url", url.strip()):
                            st.session_state.user_files_processed += 1
                            st.success(f"Processed: {url.strip()}")
        
        if st.button("Clear All Data"):
            if vector_store.clear_collections():
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
            initial_context = vector_store.query_collections("company information and user information", n_results=5)
            if initial_context:
                system_message = Prompts.create_system_message(initial_context)
                initial_messages = [system_message]
                
                # Get initial response
                response = clients.llm(initial_messages)
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
                context = vector_store.query_collections(user_input)
                
                # Update system message with new context
                st.session_state.messages[0] = Prompts.create_system_message(context)
            
                # Get AI response
                response = clients.llm(st.session_state.messages)
                st.session_state.messages.append(AIMessage(content=response.content))
                st.chat_message("assistant").write(response.content)
                
                # Check for conversation end
                if "have a great day" in response.content.lower():
                    st.session_state.conversation_ended = True
                    st.rerun()

if __name__ == "__main__":
    main()