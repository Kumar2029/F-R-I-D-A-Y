import json
import os
from datetime import datetime

HEALTH_FILE = "memory/strategy_health.json"

class StrategyHealth:
    def __init__(self):
        os.makedirs("memory", exist_ok=True)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(HEALTH_FILE):
            with open(HEALTH_FILE, "w") as f:
                json.dump({}, f)

    def _load(self):
        with open(HEALTH_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}

    def _save(self, data):
        with open(HEALTH_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def record_failure(self, strategy_id):
        data = self._load()
        if strategy_id not in data:
            data[strategy_id] = {"failures": 0, "quarantined": False, "last_failure": None}
        
        data[strategy_id]["failures"] += 1
        data[strategy_id]["last_failure"] = datetime.utcnow().isoformat()
        
        # Quarantine Logic
        if data[strategy_id]["failures"] >= 3:
            data[strategy_id]["quarantined"] = True
            print(f"[StrategyHealth] {strategy_id} quarantined due to {data[strategy_id]['failures']} consecutive failures.")
        else:
            print(f"[StrategyHealth] {strategy_id} failure count: {data[strategy_id]['failures']}")
            
        self._save(data)

    def record_success(self, strategy_id):
        data = self._load()
        if strategy_id in data:
            # Reset on success
            data[strategy_id]["failures"] = 0
            if data[strategy_id]["quarantined"]:
                print(f"[StrategyHealth] {strategy_id} released from quarantine due to success.")
            data[strategy_id]["quarantined"] = False
            self._save(data)

    def is_quarantined(self, strategy_id):
        data = self._load()
        if strategy_id not in data:
            return False
        return data[strategy_id].get("quarantined", False)
