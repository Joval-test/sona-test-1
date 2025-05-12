import streamlit as st
import pandas as pd

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

def format_user_content(user_data):
    return (f"Status: {user_data['Status (Hot/Warm/Cold/Not Responded)']}\n"
            f"ID: {user_data['ID']}\n"
            f"Name: {user_data['Name']}\n"
            f"Company: {user_data['Company']}\n"
            f"Email: {user_data['Email']}\n"
            f"Description: {user_data['Description']}\n"
            f"Source: {user_data['source']}\n"
            f"Connected: {user_data['Connected']}\n"
            f"Chat Summary: {user_data['Chat Summary']}")