import asyncio
import json
import os
from unittest.mock import MagicMock
from Backend.contracts import Goal, Strategy
from Backend.StrategyHealth import StrategyHealthManager, StrategyHealth
from Backend.StrategySelector import StrategySelector

HEALTH_FILE = "memory/strategy_health.json"

def setup_clean_state():
    if os.path.exists(HEALTH_FILE):
        os.remove(HEALTH_FILE)
    print("\n[Setup] Cleaned health memory.")

def test_persistence():
    print("\n[Test] Strategy Health Persistence")
    setup_clean_state()
    
    mgr = StrategyHealthManager()
    mgr.record_success("test_strategy")
    mgr.record_failure("test_strategy")
    
    # Reload
    mgr2 = StrategyHealthManager()
    health = mgr2.get_health("test_strategy")
    
    print(f"Health: Success={health.success_count}, Failures={health.failure_count}, Score={health.score}")
    
    if health.success_count == 1 and health.failure_count == 1 and health.score == 0.5:
        print("SUCCESS: Persistence verified.")
    else:
        print("FAILED: Persistence check.")

def test_adaptive_ranking_and_failsafe():
    print("\n[Test] Adaptive Ranking & Fail-Safe")
    setup_clean_state()
    
    # Simulate a failing strategy directly in JSON to save time
    data = {
        "send_whatsapp": {"success_count": 0, "failure_count": 10}, # Score 0.0
        "send_sms": {"success_count": 5, "failure_count": 0}        # Score 1.0 (if it exists)
    }
    with open(HEALTH_FILE, "w") as f:
        json.dump(data, f)
        
    selector = StrategySelector()
    
    # CASE 1: WhatsApp is failing (Score 0.0) -> Should trigger Fail-Safe (or pick next if implemented)
    # Our implementation currently only has "send_whatsapp" candidate for send_message.
    # So it should return ask_user due to low score.
    
    goal = Goal(name="send_message", target="Mom", priority="normal")
    strategy = selector.select_strategy(goal)
    
    print(f"Case 1 Strategy: {strategy.name}")
    if strategy.name == "ask_user" and "Score" in strategy.reason:
        print("SUCCESS: Fail-Safe triggered for low score.")
    else:
        print(f"FAILED: Expected ask_user/Fail-Safe, got {strategy.name}")
    
    # CASE 2: Restore health
    data["send_whatsapp"] = {"success_count": 10, "failure_count": 0} # Score 1.0
    with open(HEALTH_FILE, "w") as f:
        json.dump(data, f)
        
    # Reload (Manager caches, so need new instance or reload logic. Manager loads in __init__)
    selector = StrategySelector() 
    strategy = selector.select_strategy(goal)
    
    print(f"Case 2 Strategy: {strategy.name}")
    if strategy.name == "send_whatsapp":
        print("SUCCESS: Healthy strategy selected.")
    else:
        print(f"FAILED: Expected send_whatsapp, got {strategy.name}")

if __name__ == "__main__":
    test_persistence()
    test_adaptive_ranking_and_failsafe()
