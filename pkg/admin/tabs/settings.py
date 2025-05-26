import streamlit as st
import os
import base64
from pkg.shared.core.data_processor import process_company_files, process_company_urls, process_user_files, display_file_details
from pkg.shared.core.vector_store import clear_collections
from pkg.shared import config
import pandas as pd
from pkg.shared.core.stage_logger import stage_log


@stage_log(stage=2)
def setup_company_section():
    st.header("Company Information")
    company_source = st.radio("Select company info source:", ["PDF", "URL"])
    
    if company_source == "PDF":
        company_files = st.file_uploader(
            "Upload company information PDFs",
            type="pdf",
            accept_multiple_files=True
        )
        if company_files and st.button("Process Company Files"):
            process_company_files(company_files)
    
    elif company_source == "URL":
        company_urls = st.text_area("Enter company website URLs (one per line):")
        if company_urls and st.button("Process Company URLs"):
            process_company_urls(company_urls)


@stage_log(stage=2)
def setup_user_section():
    st.header("User Information")
    
    # Create data directory and MASTER_PATH if they don't exist
    master_dir = os.path.dirname(config.MASTER_PATH)
    if not os.path.exists(master_dir):
        os.makedirs(master_dir)
    
    if not os.path.exists(config.MASTER_PATH):
        # Create empty Excel file with required columns
        empty_df = pd.DataFrame(columns=[
            'ID', 'Name', 'Company', 'Email', 'Description', 'source'
        ])
        empty_df.to_excel(config.MASTER_PATH, index=False)
    
    user_files = st.file_uploader(
        label="Upload user data files",
        type=['xlsx', 'xls', 'csv'],
        help="Required columns: ID, Name, Company, Email, Description",
        accept_multiple_files=True
    )
    if user_files and st.button("Process User Files"):
        process_user_files(user_files)


@stage_log(stage=2)
def setup_env_section():
    env_keys = [
        "EMAIL_SENDER", "EMAIL_PASSWORD",
        "AZURE_ENDPOINT", "AZURE_API_KEY", "AZURE_API_VERSION", "AZURE_DEPLOYMENT", "AZURE_EMBEDDING_DEPLOYMENT"
    ]
    st.header("Email Settings")
    with st.expander("Email Settings", expanded=False):
        email = st.text_input("Sender Email", value=st.session_state.get("EMAIL_SENDER", ""), key="email_sender")
        password = st.text_input("Email Password", type="password", value=st.session_state.get("EMAIL_PASSWORD", ""), key="email_password")
        if st.button("Save Email Settings"):
            config.save_settings_to_env_and_state(
                EMAIL_SENDER=email,
                EMAIL_PASSWORD=password
            )
            st.success("Email settings saved successfully!")
            st.session_state.page = "Connect"
            st.rerun()

    st.header("Azure Settings")
    with st.expander("Azure Deployment Settings", expanded=False):
        azure_endpoint = st.text_input("Azure Endpoint", value=st.session_state.get("AZURE_ENDPOINT", ""), key="azure_endpoint")
        azure_api_key = st.text_input("Azure API Key", value=st.session_state.get("AZURE_API_KEY", ""), key="azure_api_key")
        azure_api_version = st.text_input("Azure API Version", value=st.session_state.get("AZURE_API_VERSION", ""), key="azure_api_version")
        azure_deployment = st.text_input("Azure Deployment", value=st.session_state.get("AZURE_DEPLOYMENT", ""), key="azure_deployment")
        azure_embedding_deployment = st.text_input("Azure Embedding Deployment", value=st.session_state.get("AZURE_EMBEDDING_DEPLOYMENT", ""), key="azure_embedding_deployment")
        if st.button("Save Azure Settings"):
            config.save_settings_to_env_and_state(
                AZURE_ENDPOINT=azure_endpoint,
                AZURE_API_KEY=azure_api_key,
                AZURE_API_VERSION=azure_api_version,
                AZURE_DEPLOYMENT=azure_deployment,
                AZURE_EMBEDDING_DEPLOYMENT=azure_embedding_deployment
            )
            st.success("Azure settings saved successfully!")
            st.session_state.page = "Connect"
            st.rerun()


@stage_log(stage=1)
def render_page():
    with open(config.ICON_PATH, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
        image_and_heading_html = f"""
        <div style="display: flex; justify-content:center;background:white">
            <img src="data:image/png;base64,{encoded_image}" style="width: 75px; height: 75px; object-fit: contain; position: relative; left: -37px;">
            <h1 style="font-size: 2rem; margin: 0; z-index: 2; position: relative; left: -32px; top: -5px; color: #BE232F;">
                    Caze <span style="color: #304654;">BizConAI</span>
        </div>
        """
        st.markdown(image_and_heading_html, unsafe_allow_html=True)
    # Only show upload sections if Azure credentials are present
    required_vars = [
        st.session_state.get("AZURE_ENDPOINT", ""),
        st.session_state.get("AZURE_API_KEY", ""),
        st.session_state.get("AZURE_API_VERSION", ""),
        st.session_state.get("AZURE_DEPLOYMENT", "")
    ]
    setup_env_section()
    if all(required_vars):
        setup_company_section()
        if "company_collection" in st.session_state and st.session_state.company_collection:
            display_file_details(st.session_state.company_collection)
        setup_user_section()
        if st.button("Clear All Data"):
            if clear_collections(st.session_state.company_collection):
                if os.path.exists(config.MASTER_PATH):
                    os.remove(config.MASTER_PATH)
                st.rerun()