import streamlit as st
import langchain
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from ui_components import *
from clients import *
from vector_store import *
from data_processor import *
from prompts import *
import config

def main():
    langchain.debug = True
    
    initialize_session_state()
    setup_header()
    
    if not st.session_state.hide_info_bar:
        st.info("👈 Let's start by uploading the informations of the company and the user.")
    
    llm = initialize_llm()
    embeddings = initialize_embeddings()
    company_collection, user_collection = initialize_collections(embeddings)

    st.session_state.company_collection = company_collection
    st.session_state.user_collection = user_collection
    
    setup_sidebar()
    
    button_container = st.empty()
    if button_container.button('Start Conversation'):
        handle_conversation_start(button_container, llm, embeddings, company_collection, user_collection)
    
    if st.session_state.show_chat:
        handle_chat_interface(llm, embeddings, company_collection, user_collection)

if __name__ == "__main__":
    main()