import json
import os
from dataclasses import dataclass, asdict

HEALTH_FILE = "memory/strategy_health.json"

@dataclass
class StrategyHealth:
    success_count: int = 0
    failure_count: int = 0
    consecutive_failures: int = 0
    cooldown_remaining: int = 0

    @property
    def score(self) -> float:
        # Standardized Score Logic: Success raises score, Failure lowers it (simple ratio)
        # Default 1.0, drops with failures.
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0  # Optimistic start
        return self.success_count / total

class StrategyHealthManager:
    def __init__(self):
        os.makedirs("memory", exist_ok=True)
        self.health_map = {} # Cache
        self._load()

    def _load(self):
        if not os.path.exists(HEALTH_FILE):
             self.health_map = {}
             return

        try:
            with open(HEALTH_FILE, "r") as f:
                raw_data = json.load(f)
                # Convert raw dicts to StrategyHealth objects
                for strategy, stats in raw_data.items():
                    self.health_map[strategy] = StrategyHealth(
                        success_count=stats.get("success_count", 0),
                        failure_count=stats.get("failure_count", 0),
                        consecutive_failures=stats.get("consecutive_failures", 0),
                        cooldown_remaining=stats.get("cooldown_remaining", 0)
                    )
        except Exception as e:
            print(f"[StrategyHealth] Load failed: {e}")
            self.health_map = {}

    def _save(self):
        try:
            # Convert objects back to dicts
            data = {
                strategy: {
                    "success_count": h.success_count, 
                    "failure_count": h.failure_count,
                    "consecutive_failures": h.consecutive_failures,
                    "cooldown_remaining": h.cooldown_remaining
                }
                for strategy, h in self.health_map.items()
            }
            with open(HEALTH_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[StrategyHealth] Save failed: {e}")

    def get_health(self, strategy_name: str) -> StrategyHealth:
        if strategy_name not in self.health_map:
             self.health_map[strategy_name] = StrategyHealth()
        return self.health_map[strategy_name]

    def record_success(self, strategy_name: str):
        health = self.get_health(strategy_name)
        health.success_count += 1
        health.failure_count = 0 # failures = 0 requested, mapping to failure_count
        health.consecutive_failures = 0
        health.cooldown_remaining = 0
        self._save()
        print(f"[StrategyHealth] {strategy_name} SUCCESS. New Score: {health.score:.2f}")

    def record_failure(self, strategy_name: str):
        health = self.get_health(strategy_name)
        health.failure_count += 1 
        health.consecutive_failures += 1
        
        if health.consecutive_failures >= 4: # Relaxed from 2 (Part C)
            health.cooldown_remaining = 3
            print(f"[StrategyHealth] {strategy_name} FROZEN (Cooldown: 3)")
            
        self._save()
        print(f"[StrategyHealth] {strategy_name} FAILURE. New Score: {health.score:.2f}")

