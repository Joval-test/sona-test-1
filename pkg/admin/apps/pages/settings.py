import streamlit as st
import os
import base64
from shared.core.data_processor import process_company_files, process_company_urls, process_user_files, display_file_details
from shared.core.vector_store import clear_collections
from shared import config
import pandas as pd
from apps.utils.stage_logger import stage_log


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
def setup_email_section():
    st.header("Email Configuration")
    with st.expander("Email Settings"):
        email = st.text_input("Sender Email")
        password = st.text_input("Email Password", type="password")
        
        if st.button("Save Email Settings"):
            if email and password:
                try:
                    # Create or update .env file
                    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
                    
                    # Read existing env file content
                    env_content = ""
                    if os.path.exists(env_path):
                        with open(env_path, 'r') as f:
                            lines = f.readlines()
                            # Remove existing email settings if any
                            lines = [line for line in lines if not line.startswith(('EMAIL_SENDER=', 'EMAIL_PASSWORD='))]
                            env_content = ''.join(lines)
                    
                    # Append new email settings
                    env_content += f"\nEMAIL_SENDER=\"{email}\"\nEMAIL_PASSWORD=\"{password}\""
                    
                    with open(env_path, 'w') as f:
                        f.write(env_content.strip())
                        
                    st.success("Email settings saved successfully!")
                    # Force Streamlit to rerun to load new environment variables
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save email settings: {str(e)}")
            else:
                st.error("Please provide both email and password")


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
    st.header("LLM Configuration")
    model_options = ["Azure OpenAI", "Llama 3.1", "Phi3.5", "Mistral", "Deepseek"]
    selected_model = st.selectbox("Select LLM Model:", model_options)
    
    if st.button("Save Configuration"):
        st.success(f"LLM updated to {selected_model} successfully!")
    
    setup_email_section()
    setup_company_section()
    
    if st.session_state.company_collection:
        display_file_details(st.session_state.company_collection)
    
    setup_user_section()
    
    if st.button("Clear All Data"):
        if clear_collections(st.session_state.company_collection):
            if os.path.exists(config.MASTER_PATH):
                os.remove(config.MASTER_PATH)
            st.rerun()