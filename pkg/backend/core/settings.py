import os
from dotenv import load_dotenv, set_key
from core.vector_store import clear_company_collection
from core.utils import clear_data_dir
from logging_utils import stage_log
import logging

logger = logging.getLogger(__name__)

DATA_DIR = 'data'

def get_env_path():
    """Get absolute path to .env file"""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def ensure_env_file():
    """Create .env file with default values if it doesn't exist"""
    env_path = get_env_path()
    
    if not os.path.exists(env_path):
        logger.info("Creating new .env file with default values")
        default_settings = {
            'EMAIL_SENDER': '',
            'EMAIL_PASSWORD': '',
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_PORT': '587',
            'AZURE_ENDPOINT': '',
            'AZURE_API_KEY': '',
            'AZURE_API_VERSION': '2025-01-01-preview',
            'AZURE_DEPLOYMENT': 'gpt-4o-mini-apr09',
            'AZURE_EMBEDDING_DEPLOYMENT': 'text-embedding-large-new',
            'PRIVATE_LINK_BASE': 'http://127.0.0.1:5000',
            'PRIVATE_LINK_PATH': '/chat?user='
        }
        
        try:
            with open(env_path, 'w') as f:
                for key, value in default_settings.items():
                    f.write(f'{key}={value}\n')
            logger.info(".env file created successfully")
        except Exception as e:
            logger.error(f"Error creating .env file: {e}")
            raise

    return env_path

# Initialize env file
env_path = ensure_env_file()
load_dotenv(env_path)

@stage_log(2)
def save_email_settings(data):
    try:
        # Get path to .env file
        env_path = get_env_path()
        
        # Validate data
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")

        sender = data.get('sender')
        password = data.get('password')
        
        if not sender or not password:
            raise ValueError("Missing email sender or password")
        
        # Update values
        set_key(env_path, 'EMAIL_SENDER', sender)
        set_key(env_path, 'EMAIL_PASSWORD', password)
        
        # Optional SMTP settings with defaults
        set_key(env_path, 'EMAIL_HOST', data.get('host', 'smtp.gmail.com'))
        set_key(env_path, 'EMAIL_PORT', str(data.get('port', 587)))

        # Reload environment variables
        load_dotenv(env_path)
        
        return {"success": True, "message": "Email settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving email settings: {e}")
        return {"success": False, "message": str(e)}

@stage_log(2)
def save_azure_settings(data):
    try:
        env_path = get_env_path()
        
        # Validate data
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")

        # Update values
        set_key(env_path, 'AZURE_ENDPOINT', data.get('endpoint', ''))
        set_key(env_path, 'AZURE_API_KEY', data.get('api_key', ''))
        set_key(env_path, 'AZURE_API_VERSION', data.get('api_version', ''))
        set_key(env_path, 'AZURE_DEPLOYMENT', data.get('deployment', ''))
        set_key(env_path, 'AZURE_EMBEDDING_DEPLOYMENT', data.get('embedding_deployment', ''))
        
        # Reload environment variables
        load_dotenv(env_path)
        
        return {'success': True, 'message': 'Azure settings saved successfully'}
    except Exception as e:
        logger.error(f"Error saving Azure settings: {e}")
        return {'success': False, 'message': str(e)}

def get_settings():
    try:
        # Ensure .env file exists and reload
        env_path = ensure_env_file()
        load_dotenv(env_path)
        
        return {
            "email_sender": os.getenv('EMAIL_SENDER', ''),
            "email_host": os.getenv('EMAIL_HOST', 'smtp.gmail.com'),
            "email_port": int(os.getenv('EMAIL_PORT', '587')),
            "azure_endpoint": os.getenv('AZURE_ENDPOINT', ''),
            "azure_api_key": os.getenv('AZURE_API_KEY', ''),
            "azure_api_version": os.getenv('AZURE_API_VERSION', ''),
            "azure_deployment": os.getenv('AZURE_DEPLOYMENT', ''),
            "azure_embedding_deployment": os.getenv('AZURE_EMBEDDING_DEPLOYMENT', ''),
            "private_link_base": os.getenv('PRIVATE_LINK_BASE', ''),
            "private_link_path": os.getenv('PRIVATE_LINK_PATH', '')
        }
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return {"success": False, "message": str(e)}

@stage_log(1)
def clear_all_data():
    clear_data_dir(DATA_DIR)
    clear_company_collection()
    return {'success': True, 'message': 'All data cleared'}

@stage_log(3)
def get_private_link_config():
    env_path = get_env_path()
    load_dotenv(env_path)
    return {
        'base': os.getenv('PRIVATE_LINK_BASE', 'https://127.0.0.1:5000'),
        'path': os.getenv('PRIVATE_LINK_PATH', '/chat?user=')
    }

@stage_log(2)
def save_private_link_config(data):
    try:
        env_path = get_env_path()
        
        # Validate data
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")
        
        # Update values
        set_key(env_path, 'PRIVATE_LINK_BASE', data.get('base', 'https://127.0.0.1:5000'))
        set_key(env_path, 'PRIVATE_LINK_PATH', data.get('path', '/chat?user='))
        
        # Reload environment variables
        load_dotenv(env_path)
        
        return {'success': True, 'message': 'Private link settings saved successfully'}
    except Exception as e:
        logger.error(f"Error saving private link settings: {e}")
        return {'success': False, 'message': str(e)}

@stage_log(3)
def get_report_path():
    return os.path.join(DATA_DIR, 'report.xlsx')
