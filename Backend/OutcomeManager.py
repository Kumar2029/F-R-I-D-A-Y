import json
import os
from datetime import datetime

OUTCOME_FILE = "memory/outcomes.json"

class OutcomeManager:
    def __init__(self, memory_dir=None):
        # Allow memory_dir argument for compatibility but force strict outcome file path
        os.makedirs("memory", exist_ok=True)
        if not os.path.exists(OUTCOME_FILE):
            with open(OUTCOME_FILE, "w") as f:
                json.dump([], f)

    def record(self, goal_id, target, strategy, primary_success, time_taken, retries, fallback_used):
        # PART 1: Fix Outcome Semantics
        # Fallback = damage control, not success.
        success = primary_success 

        # PART 2 Integration: Update Strategy Health
        from Backend.StrategyHealth import StrategyHealth
        health_mgr = StrategyHealth()
        
        if success:
            health_mgr.record_success(strategy)
        else:
            # If primary failed (even if fallback worked), it's a strategy failure
            health_mgr.record_failure(strategy)

        outcome = {
            "timestamp": datetime.utcnow().isoformat(),
            "goal_id": goal_id,
            "target": target,
            "strategy": strategy,
            "success": success,
            "fallback_used": fallback_used,
            "time_taken": time_taken,
            "retries": retries,
            "confidence": self._calculate_confidence(success, time_taken, retries)
        }

        with open(OUTCOME_FILE, "r+") as f:
            data = json.load(f)
            data.append(outcome)
            f.seek(0)
            json.dump(data, f, indent=2)

        return outcome["confidence"]

    def _calculate_confidence(self, success, time_taken, retries, expected_time=6.0):
        return round(
            0.6 * (1.0 if success else 0.0) +
            0.2 * max(0, 1 - retries / 3) +
            0.2 * max(0, 1 - time_taken / expected_time),
            3
        )

    def recent_outcomes(self, goal_id, target=None, limit=5):
        with open(OUTCOME_FILE) as f:
            data = json.load(f)

        filtered = [
            o for o in reversed(data)
            if o["goal_id"] == goal_id and (target is None or o["target"] == target)
        ]

        return filtered[:limit]
    
    # Keeping compatibility methods if referenced elsewhere, but prioritizing strict implementation above.
    # Previous code referenced get_strategy_stats and save_outcome.
    # I should check if StrategySelector uses get_strategy_stats.
    # Yes, StrategySelector uses: stats = self.outcome_manager.get_strategy_stats("send_whatsapp")
    # THE USER SAID: "Implement EXACTLY: ... (the code)"
    # But later: "Modify Backend/StrategySelector.py ... import OutcomeManager ... bias_strategy logic"
    # The new StrategySelector logic doesn't use `get_strategy_stats`. It uses `recent_outcomes`.
    # "ADD this logic (DO NOT DELETE EXISTING RULES)".
    # Existing rules in StrategySelector call `get_strategy_stats`.
    # If I delete `get_strategy_stats`, existing rules might break.
    # "Existing rules in StrategySelector call `get_strategy_stats`"?
    # Let me re-read StrategySelector logic I just saw.
    # Yes, heavily uses `get_strategy_stats`.
    # User said: "Implement EXACTLY... Backend/OutcomeManager.py"
    # But also "WITHOUT breaking... GSO...".
    # If I remove `get_strategy_stats`, I break existing GSO StrategySelector logic unless I update it.
    # But Part 2 says "Modify StrategySelector... ADD this logic... DO NOT DELETE EXISTING RULES".
    # This implies existing rules using `get_strategy_stats` will persist.
    # So `OutcomeManager` MUST support `get_strategy_stats` provided it doesn't conflict.
    # But strict instruction "Implement EXACTLY" for OutcomeManager file usually implies "Replace content".
    # Hybrid approach: I will Implement EXACTLY the new class structure, but I will ADD BACK `get_strategy_stats` and `save_outcome` wrapper to maintain backward compatibility for existing callers.
    # Actually, `save_outcome` is replaced by `record`. I should check where `save_outcome` is called. It is called in GoalManager.
    # Part 4 says: "AFTER execution... outcome_manager.record(...)". So GoalManager will be updated to use `record`.
    # So `save_outcome` might not be needed in GoalManager anymore.
    # What about `StrategySelector`? It calls `get_strategy_stats`.
    # I should check if I can keep `get_strategy_stats`.
    # The user gave a class `OutcomeManager`.
    # I will add `get_strategy_stats` to it to be safe, implementing it using the new data structure (which is compatible, just JSON list).
    
    def get_strategy_stats(self, strategy_id):
        # Compatibility method for existing StrategySelector logic
        with open(OUTCOME_FILE) as f:
            data = json.load(f)
        
        relevant = [x for x in data if x.get("strategy") == strategy_id or x.get("strategy_id") == strategy_id]
        if not relevant:
            return {"count": 0, "success_rate": 0.0}
        
        success_count = sum(1 for x in relevant if x.get("success", False))
        return {
            "count": len(relevant),
            "success_rate": success_count / len(relevant)
        }
    
    def save_outcome(self, outcome):
        # Compatibility wrapper for Outcome object if needed until GoalManager is fully updated
        # New GoalManager will use .record() passing primitives.
        # But old code or other places might use save_outcome(Outcome object).
        # Outcome object has attributes.
        self.record(
            goal_id=outcome.goal_id,
            target=getattr(outcome, 'target', None), # Outcome object in old code didn't have target? It used Goal ID.
            strategy=outcome.strategy_id,
            success=outcome.success,
            time_taken=outcome.time_taken,
            retries=outcome.retries,
            user_intervention=outcome.user_intervention
        )

