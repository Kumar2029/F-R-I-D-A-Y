import json
import os

class MemoryManager:
    def __init__(self):
        self.memory_dir = "memory"
        self.files = {
            "contacts": os.path.join(self.memory_dir, "contacts.json"),
            "preferences": os.path.join(self.memory_dir, "preferences.json"),
            "user_profile": os.path.join(self.memory_dir, "user_profile.json"),
            "failures": os.path.join(self.memory_dir, "failures.json")
        }
        self._initialize_memory()

    def _initialize_memory(self):
        """Create memory directory and default files if they don't exist."""
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
            print(f"Created memory directory: {self.memory_dir}")

        defaults = {
            "contacts": {},
            "preferences": {"browser": "chrome", "theme": "dark"},
            "user_profile": {"name": "User", "relationships": {}},
            "failures": []
        }

        for name, path in self.files.items():
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(defaults[name], f, indent=4)
                print(f"Initialized memory file: {path}")

    def _load_json(self, file_key):
        try:
            with open(self.files[file_key], "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_key}: {e}")
            return {}

    def _save_json(self, file_key, data):
        try:
            with open(self.files[file_key], "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving {file_key}: {e}")
            return False

    def get_contact(self, name):
        """Retrieve contact details by name (case-insensitive)."""
        contacts = self._load_json("contacts")
        name_lower = name.lower()
        return contacts.get(name_lower)

    def add_contact(self, name, details):
        """Add or update a contact."""
        contacts = self._load_json("contacts")
        contacts[name.lower()] = details
        return self._save_json("contacts", contacts)

    def get_preference(self, key):
        """Get a specific user preference."""
        prefs = self._load_json("preferences")
        return prefs.get(key)

    def record_failure(self, failure_data):
        """
        Record a structured failure.
        Schema: {
          "goal_type": str,
          "context": str,
          "failure_stage": str,
          "failure_reason": str,
          "timestamp": str,
          "user_aborted": bool
        }
        """
        failures = self._load_json("failures")
        # Ensure it's a list
        if not isinstance(failures, list):
            failures = []
            
        failures.append(failure_data)
        self._save_json("failures", failures)

    def get_failures(self):
        return self._load_json("failures")

    def get_failures_by_goal(self, goal_type):
        """Retrieve all failures matching a specific goal type."""
        entry_list = self._load_json("failures")
        if not isinstance(entry_list, list):
            return []
        
        return [f for f in entry_list if f.get("goal_type") == goal_type]
