import json
import os

CONTACTS_FILE = "FRIDAY/memory/contacts.json"

class ContactResolver:
    def __init__(self):
        self.contacts = self._load_contacts()

    def _load_contacts(self):
        if not os.path.exists(CONTACTS_FILE):
            return {}
        try:
            with open(CONTACTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

    def resolve(self, name: str) -> str:
        """
        Resolves a raw name to a contact name.
        If not found, returns the raw name (assumed to be correct).
        """
        name_lower = name.lower()
        if name_lower in self.contacts:
            return self.contacts[name_lower]
        
        # Heuristic: If name is short, it might be a nickname. 
        # For now, we trust the input if not mapped.
        return name

    def add_contact(self, nickname: str, real_name: str):
        self.contacts[nickname.lower()] = real_name
        self._save_contacts()

    def _save_contacts(self):
        os.makedirs(os.path.dirname(CONTACTS_FILE), exist_ok=True)
        with open(CONTACTS_FILE, 'w') as f:
            json.dump(self.contacts, f, indent=4)
