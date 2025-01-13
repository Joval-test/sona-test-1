import streamlit as st
import os
WORKSPACES_FOLDER = "workspaces"

def ensure_folder_exists(folder_path):
    """Ensure the folder exists. If not, create it."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def get_files_in_folder(folder_path):
    """Get a list of files in the specified folder."""
    try:
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    except Exception as e:
        st.error(f"Error reading files: {e}")
        return []

def read_file_content(file_path):
    """Read the content of the specified file."""
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        st.error(f"Could not read file: {e}")
        return ""