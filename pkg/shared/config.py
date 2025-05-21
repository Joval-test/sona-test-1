import os
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

# Updated static file paths
STATIC_DIR = os.path.join(os.getcwd(), "shared", "static")
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
MASTER_PATH = os.path.join(os.getcwd(), "data", "master_user_data.xlsx")
REPORT_PATH = os.path.join(os.getcwd(), "data", "selected_users.xlsx")
BASE_LINK = "http://127.0.0.1:8502/user_app"

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")