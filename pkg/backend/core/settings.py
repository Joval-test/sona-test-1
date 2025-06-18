import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from logging_utils import stage_log
import logging
import smtplib
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
import config

# Custom Exceptions
class InvalidCredentialsError(Exception):
    """Custom exception for invalid credentials."""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration related errors."""
    pass

class MeetingSchedulingError(Exception):
    """Custom exception for meeting scheduling related errors."""
    pass

logger = logging.getLogger(__name__)

DATA_DIR = 'data'

def validate_email_credentials(sender: str, password: str) -> None:
    """Validate email credentials by testing SMTP connection"""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.quit()
    except smtplib.SMTPAuthenticationError:
        raise InvalidCredentialsError("Invalid email credentials. Please check your email and password.")
    except Exception as e:
        raise InvalidCredentialsError(f"Failed to validate email credentials: {str(e)}")

def save_email_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save email settings to config.json"""
    try:
        # Validate credentials first
        validate_email_credentials(data["sender"], data["password"])

        # Use the batch update function for better performance
        config.save_email_settings_to_config(data["sender"], data["password"])
        
        logger.info("Email settings saved successfully")
        return {"success": True, "message": "Email settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving email settings: {str(e)}")
        raise ConfigurationError(f"Error saving email settings: {str(e)}")

def validate_azure_credentials(endpoint: str, api_key: str, api_version: str, deployment: str, embedding_deployment: str) -> None:
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
        
    except Exception as e:
        raise InvalidCredentialsError(f"Invalid Azure credentials: {str(e)}")

def save_azure_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save Azure settings to config.json"""
    try:
        # Validate credentials first
        validate_azure_credentials(
            data["endpoint"],
            data["api_key"],
            data["api_version"],
            data["deployment"],
            data["embedding_deployment"]
        )

        # Use the batch update function for better performance
        config.save_azure_settings_to_config(
            data["endpoint"],
            data["api_key"],
            data["api_version"],
            data["deployment"],
            data["embedding_deployment"]
        )
        
        logger.info("Azure settings saved successfully")
        return {"success": True, "message": "Azure settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving Azure settings: {str(e)}")
        raise ConfigurationError(f"Error saving Azure settings: {str(e)}")

def clear_all_data() -> Dict[str, Any]:
    """Clear all data from the application."""
    try:
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
        raise ConfigurationError(f"Failed to clear data: {str(e)}")

def get_private_link_config() -> Dict[str, Any]:
    """Get private link configuration (base and path only)"""
    try:
        # No need for importlib.reload with JSON config - values are always fresh
        config_data = {
            "base": config.PRIVATE_LINK_BASE,
            "path": config.PRIVATE_LINK_PATH,
        }
        return {"success": True, "config": config_data}
    except Exception as e:
        logger.error(f"Error getting private link configuration: {str(e)}")
        raise ConfigurationError(f"Error getting private link configuration: {str(e)}")

def save_private_link_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save private link configuration (base and path only) to config.json"""
    try:
        # Use the batch update function for better performance
        config.save_private_link_settings_to_config(
            data.get("base", ""),
            data.get("path", "")
        )
        
        logger.info("Private link settings saved successfully")
        return {"success": True, "message": "Private link settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving private link settings: {str(e)}")
        raise ConfigurationError(f"Error saving private link settings: {str(e)}")

def save_owner_settings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save default owner settings to config.json"""
    try:
        config.save_owner_settings_to_config(
            data.get("name", ""),
            data.get("email", "")
        )
        
        logger.info("Owner settings saved successfully")
        return {"success": True, "message": "Owner settings saved successfully"}
    except Exception as e:
        logger.error(f"Error saving owner settings: {str(e)}")
        raise ConfigurationError(f"Error saving owner settings: {str(e)}")

def get_all_config() -> Dict[str, Any]:
    """Get all configuration values"""
    try:
        all_config = config._config_manager.get_all_config()
        # Mask sensitive information in logs
        safe_config = all_config.copy()
        if safe_config.get("AZURE_OPENAI_API_KEY"):
            safe_config["AZURE_OPENAI_API_KEY"] = "*" * len(safe_config["AZURE_OPENAI_API_KEY"])
        if safe_config.get("EMAIL_PASSWORD"):
            safe_config["EMAIL_PASSWORD"] = "*" * len(safe_config["EMAIL_PASSWORD"])
        
        return {"success": True, "config": all_config}
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        raise ConfigurationError(f"Error getting configuration: {str(e)}")

@stage_log(3)
def get_report_path():
    return os.path.join(DATA_DIR, 'report.xlsx')

def setup_llm_and_embeddings():
    # No need for importlib.reload with JSON config - values are always fresh
    azure_endpoint = config.AZURE_OPENAI_ENDPOINT
    azure_deployment = config.AZURE_OPENAI_DEPLOYMENT_NAME
    azure_api_version = config.AZURE_OPENAI_API_VERSION
    azure_api_key = config.AZURE_OPENAI_API_KEY
    azure_embedding_deployment = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    
    logger.info(f"Attempting to set up LLM and embeddings with:")
    logger.info(f"azure_endpoint: {azure_endpoint}")
    logger.info(f"azure_deployment: {azure_deployment}")
    logger.info(f"azure_api_version: {azure_api_version}")
    logger.info(f"azure_api_key: {'*' * len(azure_api_key) if azure_api_key else 'N/A'}") # Mask API key
    logger.info(f"azure_embedding_deployment: {azure_embedding_deployment}")

    embeddings = None
    llm = None

    try:
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_embedding_deployment,
            openai_api_version=azure_api_version,
            api_key=azure_api_key,
            max_retries=1
        )
        # Test with a simple embedding to ensure connectivity
        embeddings.embed_query("test")
        logger.info("Azure OpenAI Embeddings initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Azure OpenAI Embeddings: {e}")
        raise ConfigurationError(f"Failed to initialize Azure OpenAI Embeddings: {e}")

    try:
        llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            api_version=azure_api_version,
            api_key=azure_api_key,
            temperature=0.1,
            max_retries=1
        )
        # Test with a simple completion to ensure connectivity
        llm.invoke("test")
        logger.info("Azure Chat OpenAI LLM initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Chat OpenAI LLM: {e}")
        raise ConfigurationError(f"Failed to initialize Azure Chat OpenAI LLM: {e}")
    
    return llm, embeddings