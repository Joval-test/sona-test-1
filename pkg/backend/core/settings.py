import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key
from core.vector_store import clear_company_collection
from core.utils import clear_data_dir
from logging_utils import stage_log
import logging
from cryptography.fernet import Fernet
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import smtplib
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

logger = logging.getLogger(__name__)

DATA_DIR = 'data'

# Encryption key derivation
def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def get_env_file_path() -> str:
    """Return the absolute path to the .env file in the backend directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

def get_encryption_key() -> tuple[Fernet, bytes]:
    """Get or create encryption key"""
    env_file = get_env_file_path()
    # Load existing key if available
    if os.path.exists(env_file):
        load_dotenv(env_file)
        key_str = os.getenv('ENCRYPTION_KEY')
        salt_str = os.getenv('ENCRYPTION_SALT')
        if key_str and salt_str:
            try:
                key = base64.urlsafe_b64decode(key_str.encode())
                salt = base64.urlsafe_b64decode(salt_str.encode())
                return Fernet(key), salt
            except Exception as e:
                logger.error(f"Error loading encryption key: {str(e)}")
    # Generate new key
    master_password = os.urandom(32).hex()  # Generate a random master password
    key, salt = derive_key(master_password)
    # Save the key and salt
    with open(env_file, 'a') as f:
        f.write(f"\nENCRYPTION_KEY={base64.urlsafe_b64encode(key).decode()}")
        f.write(f"\nENCRYPTION_SALT={base64.urlsafe_b64encode(salt).decode()}")
    return Fernet(key), salt

def encrypt_value(value: str) -> str:
    """Encrypt a string value"""
    if not value:
        return value
    try:
        fernet, _ = get_encryption_key()
        return fernet.encrypt(value.encode()).decode()
    except Exception as e:
        logger.error(f"Error encrypting value: {str(e)}")
        return value

def decrypt_value(value: str) -> str:
    """Decrypt a string value"""
    if not value:
        return value
    try:
        fernet, _ = get_encryption_key()
        return fernet.decrypt(value.encode()).decode()
    except Exception as e:
        logger.error(f"Error decrypting value: {str(e)}")
        return value

def ensure_env_file() -> None:
    """Create .env file if it doesn't exist"""
    env_file = get_env_file_path()
    if not os.path.exists(env_file):
        logger.info("Creating .env file with default values")
        default_env = """
# Email Settings
EMAIL_SENDER=
EMAIL_PASSWORD=
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# Azure OpenAI Settings
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=

# Encryption Settings
ENCRYPTION_KEY=
ENCRYPTION_SALT=
"""
        try:
            with open(env_file, 'w') as f:
                f.write(default_env.strip())
            logger.info("Successfully created .env file")
        except Exception as e:
            logger.error(f"Error creating .env file: {str(e)}")
            raise

def validate_email_credentials(sender: str, password: str) -> Dict[str, Any]:
    """Validate email credentials by testing SMTP connection"""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.quit()
        return {"success": True, "message": "Email credentials validated successfully"}
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "message": "Invalid email credentials. Please check your email and password."}
    except Exception as e:
        return {"success": False, "message": f"Failed to validate email credentials: {str(e)}"}

def save_email_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save email settings with encryption"""
    try:
        # Validate credentials first
        validation_result = validate_email_credentials(data["sender"], data["password"])
        if not validation_result["success"]:
            return validation_result

        env_file = get_env_file_path()
        ensure_env_file()
        # Ensure encryption key and salt are present
        get_encryption_key()
        # Read existing .env file
        env_content = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key] = value
        # Update email settings with encryption
        env_content['EMAIL_SENDER'] = encrypt_value(data["sender"])
        env_content['EMAIL_PASSWORD'] = encrypt_value(data["password"])
        # Write updated .env file, preserving key/salt
        with open(env_file, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        logger.info("Email settings saved successfully")
        return {"success": True, "message": "Email settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving email settings: {str(e)}")
        return {"success": False, "message": f"Error saving email settings: {str(e)}"}

def validate_azure_credentials(endpoint: str, api_key: str, api_version: str, deployment: str, embedding_deployment: str) -> Dict[str, Any]:
    """Validate Azure credentials by testing connection to Azure OpenAI"""
    try:
        # Test embeddings connection
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=endpoint,
            azure_deployment=embedding_deployment,
            openai_api_version=api_version,
            api_key=api_key
        )
        # Test with a simple embedding
        embeddings.embed_query("test")
        
        # Test chat completion connection
        llm = AzureChatOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_version=api_version,
            api_key=api_key,
            temperature=0.1
        )
        # Test with a simple completion
        llm.invoke("test")
        
        return {"success": True, "message": "Azure credentials validated successfully"}
    except Exception as e:
        return {"success": False, "message": f"Invalid Azure credentials: {str(e)}"}

def save_azure_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save Azure settings with encryption"""
    try:
        # Validate credentials first
        validation_result = validate_azure_credentials(
            data["endpoint"],
            data["api_key"],
            data["api_version"],
            data["deployment"],
            data["embedding_deployment"]
        )
        if not validation_result["success"]:
            return validation_result

        env_file = get_env_file_path()
        ensure_env_file()
        # Ensure encryption key and salt are present
        get_encryption_key()
        # Read existing .env file
        env_content = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key] = value
        # Update Azure settings with encryption
        env_content['AZURE_OPENAI_ENDPOINT'] = encrypt_value(data["endpoint"])
        env_content['AZURE_OPENAI_API_KEY'] = encrypt_value(data["api_key"])
        env_content['AZURE_OPENAI_API_VERSION'] = data["api_version"]
        env_content['AZURE_OPENAI_DEPLOYMENT_NAME'] = data["deployment"]
        env_content['AZURE_OPENAI_EMBEDDING_DEPLOYMENT'] = data["embedding_deployment"]
        # Write updated .env file, preserving key/salt
        with open(env_file, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        logger.info("Azure settings saved successfully")
        return {"success": True, "message": "Azure settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving Azure settings: {str(e)}")
        return {"success": False, "message": f"Error saving Azure settings: {str(e)}"}

def get_settings() -> Dict[str, Any]:
    """Get all settings with decryption"""
    try:
        env_file = get_env_file_path()
        ensure_env_file()
        
        # Load environment variables
        load_dotenv(env_file)
        
        # Get and decrypt settings
        settings = {
            "email_sender": decrypt_value(os.getenv('EMAIL_SENDER', '')),
            "email_smtp_server": os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            "email_smtp_port": os.getenv('EMAIL_SMTP_PORT', '587'),
            "azure_endpoint": decrypt_value(os.getenv('AZURE_OPENAI_ENDPOINT', '')),
            "azure_api_version": os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
            "azure_deployment_name": os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
        }
        
        return {"success": True, "settings": settings}
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        return {"success": False, "message": f"Error getting settings: {str(e)}"}

def clear_all_data() -> Dict[str, Any]:
    """Clear all data from the application."""
    try:
        # Clear .env file
        ensure_env_file()
        
        # Clear any other data files
        data_files = [
            'data/companies.json',
            'data/leads.json',
            'data/private_links.json'
        ]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted {file_path}")
        
        return {
            'success': True,
            'message': 'All data cleared successfully'
        }
    except Exception as e:
        logger.error(f"Failed to clear data: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to clear data: {str(e)}'
        }

def get_private_link_config() -> Dict[str, Any]:
    """Get private link configuration (base and path only)"""
    try:
        env_file = get_env_file_path()
        load_dotenv(env_file)
        config = {
            "base": os.getenv('PRIVATE_LINK_BASE', ''),
            "path": os.getenv('PRIVATE_LINK_PATH', ''),
        }
        return {"success": True, "config": config}
    except Exception as e:
        logger.error(f"Error getting private link configuration: {str(e)}")
        return {"success": False, "message": f"Error getting private link configuration: {str(e)}"}

def save_private_link_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save private link configuration (base and path only)"""
    try:
        env_file = get_env_file_path()
        ensure_env_file()
        # Read existing .env file
        env_content = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            # Skip other private link attributes
                            env_content[key] = value
        
        # Update private link settings
        env_content['PRIVATE_LINK_BASE'] = data.get("base", "")
        env_content['PRIVATE_LINK_PATH'] = data.get("path", "")
        
        # Write updated .env file
        with open(env_file, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        logger.info("Private link settings saved successfully")
        return {"success": True, "message": "Private link settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving private link settings: {str(e)}")
        return {"success": False, "message": f"Error saving private link settings: {str(e)}"}

@stage_log(3)
def get_report_path():
    return os.path.join(DATA_DIR, 'report.xlsx')

def load_and_set_decrypted_env():
    """
    Load .env, decrypt encrypted values, and set them in os.environ with the expected keys.
    This should be called before any code that uses credentials from the environment.
    """
    env_file = get_env_file_path()
    if not os.path.exists(env_file):
        ensure_env_file()
    # Read .env file
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    # Decrypt relevant values
    decrypted_vars = {}
    # Email
    decrypted_vars['EMAIL_SENDER'] = decrypt_value(env_vars.get('EMAIL_SENDER', ''))
    decrypted_vars['EMAIL_PASSWORD'] = decrypt_value(env_vars.get('EMAIL_PASSWORD', ''))
    decrypted_vars['EMAIL_SMTP_SERVER'] = env_vars.get('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    decrypted_vars['EMAIL_SMTP_PORT'] = env_vars.get('EMAIL_SMTP_PORT', '587')
    # Azure
    decrypted_vars['AZURE_ENDPOINT'] = decrypt_value(env_vars.get('AZURE_OPENAI_ENDPOINT', ''))
    decrypted_vars['AZURE_API_KEY'] = decrypt_value(env_vars.get('AZURE_OPENAI_API_KEY', ''))
    decrypted_vars['AZURE_API_VERSION'] = env_vars.get('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    decrypted_vars['AZURE_DEPLOYMENT'] = env_vars.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
    decrypted_vars['AZURE_EMBEDDING_DEPLOYMENT'] = env_vars.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', '')
    # Private Link (plain text)
    decrypted_vars['PRIVATE_LINK_BASE'] = env_vars.get('PRIVATE_LINK_BASE', '')
    decrypted_vars['PRIVATE_LINK_PATH'] = env_vars.get('PRIVATE_LINK_PATH', '')
    # Set in os.environ
    for k, v in decrypted_vars.items():
        os.environ[k] = v
