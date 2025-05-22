import streamlit as st
import pandas as pd
from components.stage_logger import stage_log

@stage_log(stage=2)
def match_user_data():
    if st.session_state.user_data_df is None or st.session_state.user_data_df.empty:
        return None

    if "user" in st.query_params:
        user_id = str(st.query_params["user"])
        st.session_state.userid = user_id
        matched_user = st.session_state.user_data_df[st.session_state.user_data_df['ID'].astype(str) == user_id]
        
        if not matched_user.empty:
            user_data = matched_user.iloc[0]
            st.session_state.matched_user_data = {
                'Status': user_data['Status (Hot/Warm/Cold/Not Responded)'],
                'ID': user_data['ID'],
                'Name': user_data['Name'],
                'Company': user_data['Company'],
                'Email': user_data['Email'],
                'Source': user_data['source'],
                'Connected': user_data['Connected'],
                'Chat Summary': user_data['Chat Summary']
            }
            return format_user_content(user_data)
    return None

@stage_log(stage=2)
def format_user_content(user_data):
    return (f"Status: {user_data['Status (Hot/Warm/Cold/Not Responded)']} | "
            f"ID: {user_data['ID']} | "
            f"Name: {user_data['Name']} | "
            f"Company: {user_data['Company']} | "
            f"Email: {user_data['Email']} | "
            f"Description: {user_data['Description']} | "
            f"Source: {user_data['source']} | "
            f"Connected: {user_data['Connected']} | "
            f"Chat Summary: {user_data['Chat Summary']}")