import streamlit as st
from apps.utils.stage_logger import stage_log
from shared import config
st.set_page_config(
    page_title="Caze BizConAI Admin",
    page_icon=config.ICON_PATH,
    layout="wide",
    initial_sidebar_state="expanded"
)

import langchain
import os
from shared.core.llm import initialize_llm_azure, initialize_embeddings_azure
from shared.core.vector_store import initialize_collections, process_and_store_content
from apps.utils.state import initialize_session_state
from apps.components.sidebar import render_sidebar
from apps.pages import connect, report, settings, help

@stage_log(stage=2)
def load_css():
    with open(os.path.join(config.CSS_DIR, "main.css")) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@stage_log(stage=2)
def initialize_app():
    if "initialized" not in st.session_state:
        langchain.debug = True
        initialize_session_state()
        
        llm = initialize_llm_azure()
        embeddings = initialize_embeddings_azure()
        company_collection = initialize_collections(embeddings)
        
        st.session_state.process_and_store_content = process_and_store_content
        st.session_state.company_collection = company_collection
        st.session_state.llm = llm
        st.session_state.embeddings = embeddings
        st.session_state.initialized = True
    
    return st.session_state.llm, st.session_state.embeddings

@stage_log(stage=2)
def check_directories():
    required_dirs = [
        config.PERSIST_DIRECTORY,
        config.STATIC_DIR,
        config.IMAGES_DIR,
        config.CSS_DIR,
        os.path.dirname(config.MASTER_PATH),
        os.path.dirname(config.REPORT_PATH)
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            # st.info(f"Created directory: {directory}")

@stage_log(stage=1)
def main():
    check_directories()
    load_css()
    llm, embeddings = initialize_app()
    
    render_sidebar()
    
    if st.session_state.page == "Connect":
        connect.render_page(llm, embeddings)
    elif st.session_state.page == "Report":
        report.render_page(config.REPORT_PATH)
    elif st.session_state.page == "Settings":
        settings.render_page()
    elif st.session_state.page == "Help":
        help.render_page()

if __name__ == "__main__":
    main()