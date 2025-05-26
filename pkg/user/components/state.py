import streamlit as st
from pkg.shared.core.stage_logger import stage_log

@stage_log(stage=2)
def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'conversation_ended' not in st.session_state:
        st.session_state.conversation_ended = False
    if 'phone_number' not in st.session_state:
        st.session_state.phone_number = ''
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ''
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
    if 'chat_mode' not in st.session_state:  # Add this line
        st.session_state.chat_mode = "Text"  # Add this line
    if "file_processing_log" not in st.session_state:
        st.session_state["file_processing_log"] = []
    if 'send_user_data_df' not in st.session_state:
        st.session_state.send_user_data_df = None
    if 'input_email' not in st.session_state:
        st.session_state.input_email = ""
    if 'user_data_df' not in st.session_state:
        st.session_state.user_data_df = None
    if 'matched_user_data' not in st.session_state:
        st.session_state.matched_user_data = None
    if 'input_interface_visible' not in st.session_state:
        st.session_state.input_interface_visible = True
    if 'age_warning_confirmed' not in st.session_state:
        st.session_state.age_warning_confirmed = False
    if 'email_config' not in st.session_state:
        st.session_state.email_config = {
            "sender": "",
            "password": ""
        }
    if "page" not in st.session_state:
        st.session_state.page = "Connect"
    if 'continue_choice' not in st.session_state:
        st.session_state.continue_choice = None