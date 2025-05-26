import os
from dotenv import load_dotenv, set_key
from core.vector_store import clear_company_collection
from core.utils import clear_data_dir

ENV_PATH = '.env'
DATA_DIR = 'data'

load_dotenv(ENV_PATH)

def save_email_settings(data):
    set_key(ENV_PATH, 'EMAIL_SENDER', data.get('sender', ''))
    set_key(ENV_PATH, 'EMAIL_PASSWORD', data.get('password', ''))
    return {'success': True, 'message': 'Email settings saved'}

def save_azure_settings(data):
    set_key(ENV_PATH, 'AZURE_ENDPOINT', data.get('endpoint', ''))
    set_key(ENV_PATH, 'AZURE_API_KEY', data.get('api_key', ''))
    set_key(ENV_PATH, 'AZURE_API_VERSION', data.get('api_version', ''))
    set_key(ENV_PATH, 'AZURE_DEPLOYMENT', data.get('deployment', ''))
    set_key(ENV_PATH, 'AZURE_EMBEDDING_DEPLOYMENT', data.get('embedding_deployment', ''))
    return {'success': True, 'message': 'Azure settings saved'}

def get_settings():
    load_dotenv(ENV_PATH)
    return {
        'email': {
            'sender': os.getenv('EMAIL_SENDER', ''),
            'password': os.getenv('EMAIL_PASSWORD', '')
        },
        'azure': {
            'endpoint': os.getenv('AZURE_ENDPOINT', ''),
            'api_key': os.getenv('AZURE_API_KEY', ''),
            'api_version': os.getenv('AZURE_API_VERSION', ''),
            'deployment': os.getenv('AZURE_DEPLOYMENT', ''),
            'embedding_deployment': os.getenv('AZURE_EMBEDDING_DEPLOYMENT', '')
        }
    }

def clear_all_data():
    clear_data_dir(DATA_DIR)
    clear_company_collection()
    return {'success': True, 'message': 'All data cleared'}

def get_private_link_config():
    load_dotenv(ENV_PATH)
    return {
        'base': os.getenv('PRIVATE_LINK_BASE', 'https://yourapp.com'),
        'path': os.getenv('PRIVATE_LINK_PATH', '/chat?user=')
    }

def save_private_link_config(data):
    set_key(ENV_PATH, 'PRIVATE_LINK_BASE', data.get('base', 'https://yourapp.com'))
    set_key(ENV_PATH, 'PRIVATE_LINK_PATH', data.get('path', '/chat?user='))
    return {'success': True, 'message': 'Private link config saved'}

def get_report_path():
    return os.path.join(DATA_DIR, 'report.xlsx') 