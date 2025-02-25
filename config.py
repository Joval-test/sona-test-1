import os
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_KEY")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

LOGO_PATH = os.path.join(os.getcwd(), "images", "logo_transparent.png")
CAZE_PATH = os.path.join(os.getcwd(), "images", "caze_labs_logo.png")
ICON_PATH = os.path.join(os.getcwd(), "images", "icon.png")
MASTER_PATH = os.path.join(os.getcwd(),"data","master_user_data.xlsx")
REPORT_PATH = os.path.join(os.getcwd(),"data","selected_users.xlsx")
BASE_LINK = "127.0.0.1:8502"     #Change the ip here
