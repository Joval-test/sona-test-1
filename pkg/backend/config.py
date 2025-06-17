import os
from typing import Any

# Configuration settings
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_DEPLOYMENT_NAME = ""
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = ""
AZURE_OPENAI_API_VERSION = ""
AZURE_OPENAI_API_KEY = ""
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
PRIVATE_LINK_BASE = ""
PRIVATE_LINK_PATH = ""
DEFAULT_OWNER_NAME = ""
DEFAULT_OWNER_EMAIL = ""


def update_config(key: str, value: Any) -> None:
    """Updates a configuration value in this file directly."""
    config_file_path = os.path.abspath(__file__)
    with open(config_file_path, 'r') as f:
        lines = f.readlines()

    with open(config_file_path, 'w') as f:
        for line in lines:
            if line.strip().startswith(f'{key} = '):
                if isinstance(value, str):
                    f.write(f'{key} = "{value}"\n')
                else:
                    f.write(f'{key} = {value}\n')
            else:
                f.write(line)

def get_config_value(key: str) -> Any:
    """Retrieves a configuration value from this file.
    This function is primarily for internal use if direct access to updated values is needed.
    For external use, simply import the variable directly (e.g., config.AZURE_ENDPOINT).
    """
    # Reload the module to get the latest values
    import importlib
    import sys
    if 'config' in sys.modules:
        importlib.reload(sys.modules['config'])
    
    return getattr(sys.modules['config'], key, None)