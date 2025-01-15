import os
import secret

AZURE_ENDPOINT = secret.AZURE_ENDPOINT
AZURE_API_KEY = secret.AZURE_KEY
AZURE_API_VERSION = "2024-05-01-preview"
AZURE_DEPLOYMENT = "gpt40-mini-long-context"
AZURE_EMBEDDING_DEPLOYMENT = "embedding"

PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_storage")
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

LOGO_PATH = os.path.join(os.getcwd(), "images", "logo_transparent.png")
CAZE_PATH = os.path.join(os.getcwd(), "images", "caze_labs_logo.png")
ICON_PATH = os.path.join(os.getcwd(), "images", "icon.png")
MASTER_PATH=os.path.join(os.getcwd(),"data","master_user_data.xlsx")
REPORT_PATH=os.path.join(os.getcwd(),"data","selected_users.xlsx")