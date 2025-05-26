import os
import sys
from dotenv import dotenv_values, set_key
import streamlit as st

# Determine .env path
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(base_dir, '.env')

# Keys to manage
CONFIG_KEYS = [
    "AZURE_ENDPOINT", "AZURE_API_KEY", "AZURE_API_VERSION", "AZURE_DEPLOYMENT", "AZURE_EMBEDDING_DEPLOYMENT",
    "EMAIL_SENDER", "EMAIL_PASSWORD"
]

# Load .env values into session_state at startup
def load_env_to_session_state():
    env_vars = dotenv_values(env_path)
    for key in CONFIG_KEYS:
        if key not in st.session_state:
            st.session_state[key] = env_vars.get(key, "")

load_env_to_session_state()

# Helper to save settings to both session_state and .env
def save_settings_to_env_and_state(**kwargs):
    for key, value in kwargs.items():
        if key in CONFIG_KEYS:
            st.session_state[key] = value
            set_key(env_path, key, value)

PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

# Updated static file paths
STATIC_DIR = os.path.join(os.getcwd(),"pkg","shared","static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")
CSS_DIR = os.path.join(STATIC_DIR, "css")

# Create directories if they don't exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(CSS_DIR, exist_ok=True)

# Updated image paths
LOGO_PATH = os.path.join(IMAGES_DIR, "logo_transparent.png")
CAZE_PATH = os.path.join(IMAGES_DIR, "caze_labs_logo.png")
ICON_PATH = os.path.join(IMAGES_DIR, "icon.png")

# Data paths
MASTER_PATH = os.path.join(os.getcwd(), "data", "Uploaded-Leads.xlsx")
REPORT_PATH = os.path.join(os.getcwd(), "data", "Connected-Lead-report.xlsx")
BASE_LINK = "http://127.0.0.1:8502/user_app"