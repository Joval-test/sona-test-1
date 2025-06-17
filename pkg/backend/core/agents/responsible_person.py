import os
import json
from config import DEFAULT_OWNER_NAME, DEFAULT_OWNER_EMAIL

class ResponsiblePersonAgent:
    def __init__(self, storage):
        self.storage = storage
        self.default_name = DEFAULT_OWNER_NAME
        self.default_email = DEFAULT_OWNER_EMAIL
        self.default_path = os.path.join(os.path.dirname(__file__), '../../data/default_responsible_person.json')

    def get_fallback_default(self):
        # Try to load from JSON file if it exists
        try:
            path = os.path.abspath(self.default_path)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    return {
                        "name": data.get("name", self.default_name),
                        "email": data.get("email", self.default_email)
                    }
        except Exception:
            pass
        return {"name": self.default_name, "email": self.default_email}

    def get_responsible_person(self, product_name: str) -> dict:
        """
        Get the responsible person's info for a given product.
        Args:
            product_name (str): The product name.
        Returns:
            dict: {"name": str, "email": str}
        """
        person = self.storage.get_responsible_person(product_name)
        if person and person.get("name") and person.get("email"):
            return person
        return self.get_fallback_default() 