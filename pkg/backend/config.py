import os
import json
from typing import Any, Dict
from cryptography.fernet import Fernet

CONFIG_FILE_PATH = os.path.join(os.getcwd(), 'config.json')

# 🔐 Static secret key (DO NOT expose in real environments)
STATIC_SECRET_KEY = b'JkuaQj46nXAxcGkVN-GBzehT8kLiRqOePFPeSLhctgc='  # Replace with actual key if necessary

# Default configuration values
DEFAULT_CONFIG = {
    "AZURE_OPENAI_ENDPOINT": "",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "",
    "AZURE_OPENAI_API_VERSION": "",
    "AZURE_OPENAI_API_KEY": "",
    "EMAIL_SENDER": "",
    "EMAIL_PASSWORD": "",
    "EMAIL_SMTP_SERVER": "smtp.gmail.com",
    "EMAIL_SMTP_PORT": 587,
    "PRIVATE_LINK_BASE": "",
    "PRIVATE_LINK_PATH": "",
    "DEFAULT_OWNER_NAME": "",
    "DEFAULT_OWNER_EMAIL": ""
}

# Keys to leave as plain (not encrypted)
PLAIN_KEYS = {"EMAIL_SMTP_PORT"}

class ConfigManager:
    def __init__(self):
        self._fernet = Fernet(STATIC_SECRET_KEY)
        self._ensure_config_file()

    def _ensure_config_file(self):
        if not os.path.exists(CONFIG_FILE_PATH):
            os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
            encrypted_config = self._encrypt_config(DEFAULT_CONFIG)
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(encrypted_config, f, indent=4)

    def _encrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        encrypted = {}
        for key, value in config.items():
            if key in PLAIN_KEYS:
                encrypted[key] = value
            elif isinstance(value, str):
                encrypted[key] = self._fernet.encrypt(value.encode()).decode()
            else:
                encrypted[key] = value
        return encrypted

    def _decrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        decrypted = {}
        for key, value in config.items():
            if key in PLAIN_KEYS:
                decrypted[key] = value
            elif isinstance(value, str):
                try:
                    decrypted[key] = self._fernet.decrypt(value.encode()).decode()
                except Exception:
                    decrypted[key] = value
            else:
                decrypted[key] = value
        return decrypted

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                raw_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            raw_config = DEFAULT_CONFIG.copy()
            self._save_config(raw_config)
        return self._decrypt_config(raw_config)

    def _save_config(self, config: Dict[str, Any]):
        encrypted_config = self._encrypt_config(config)
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(encrypted_config, f, indent=4)

    def get_value(self, key: str) -> Any:
        config = self._load_config()
        return config.get(key)

    def set_value(self, key: str, value: Any):
        config = self._load_config()
        config[key] = value
        self._save_config(config)

    def get_all_config(self) -> Dict[str, Any]:
        return self._load_config()

    def update_multiple(self, updates: Dict[str, Any]):
        config = self._load_config()
        config.update(updates)
        self._save_config(config)


# Global instance
_config_manager = ConfigManager()

# Backward compatibility
def update_config(key: str, value: Any) -> None:
    _config_manager.set_value(key, value)

def get_config_value(key: str) -> Any:
    return _config_manager.get_value(key)

# Batch update functions
def save_email_settings_to_config(sender: str, password: str) -> None:
    updates = {
        "EMAIL_SENDER": sender,
        "EMAIL_PASSWORD": password
    }
    _config_manager.update_multiple(updates)

def save_azure_settings_to_config(endpoint: str, api_key: str, api_version: str, 
                                  deployment: str, embedding_deployment: str) -> None:
    updates = {
        "AZURE_OPENAI_ENDPOINT": endpoint,
        "AZURE_OPENAI_API_KEY": api_key,
        "AZURE_OPENAI_API_VERSION": api_version,
        "AZURE_OPENAI_DEPLOYMENT_NAME": deployment,
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": embedding_deployment
    }
    _config_manager.update_multiple(updates)

def save_private_link_settings_to_config(base: str, path: str) -> None:
    updates = {
        "PRIVATE_LINK_BASE": base,
        "PRIVATE_LINK_PATH": path
    }
    _config_manager.update_multiple(updates)

def save_owner_settings_to_config(name: str, email: str) -> None:
    updates = {
        "DEFAULT_OWNER_NAME": name,
        "DEFAULT_OWNER_EMAIL": email
    }
    _config_manager.update_multiple(updates)

def __getattr__(name: str) -> Any:
    if name in DEFAULT_CONFIG:
        return _config_manager.get_value(name)
    raise AttributeError(f"'{__name__}' has no attribute '{name}'")

__all__ = [
    'update_config',
    'get_config_value',
    'ConfigManager',
    '_config_manager',
    'save_email_settings_to_config',
    'save_azure_settings_to_config',
    'save_private_link_settings_to_config',
    'save_owner_settings_to_config'
]
