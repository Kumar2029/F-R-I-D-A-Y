
import sys
import os
import time
sys.path.append(os.getcwd())

# Mock Automation to prevent real app opening
import Backend.Automation
original_open = Backend.Automation.OpenApp
def mock_open(app):
    print(f"[MOCK] Opening {app}")
    return True
Backend.Automation.OpenApp = mock_open

# Mock OutcomeVerifier
import Backend.OutcomeVerifier
Backend.OutcomeVerifier.OutcomeVerifier.verify_outcome = lambda self, criteria: (True, "Mock Success")

from Backend.GoalManager import GoalManager
from rich import print

def test_v4_loop():
    gm = GoalManager()
    
    print("\n=== TEST 1: Standard Execution (aligned) ===")
    # Query: Open Calculator (Expectation: Open)
    # Planner likely returns Open Calculator
    gm.create_goal("Open Calculator")
    res = gm.execute_goal(list(gm.active_goals.keys())[0])
    print(f"Result: {res}")
    
    context = gm.context_engine.get_context()
    print(f"Context after success: {gm.context_engine.format_context()}")

    print("\n=== TEST 2: Repetition (Context Shift) ===")
    # Repeat same goal 3 times
    for i in range(3):
        print(f"\n--- Repetition {i+1} ---")
        gm.create_goal("Open Calculator") # Description matches last
        gm.execute_goal(list(gm.active_goals.keys())[-1])
        
    context = gm.context_engine.get_context()
    print(f"Context after repetitions: {gm.context_engine.format_context()}")
    
    if context['autonomy_level'] < 0.5:
        print("[PASS] Autonomy dropped due to repetitions.")
    else:
        print("[FAIL] Autonomy did not drop significantly.")

    print("\n=== TEST 3: High Mismatch (Should Block/Warn) ===")
    # We need to simulate a Planner hallucination or valid plan that mismatches expectation.
    # Since we can't easily force the real Planner (Cohere) to hallucinate on command without a bad prompt,
    # we will manually inject a bad plan into the goal right after planning phase?
    # Or cleaner: We just check if Verifier blocks it by calling Verifier directly with mismatching data,
    # OR we trust our previous unit test for Verifier and just run a goal we know creates mismatch if we can.
    # "Open WhatsApp" -> If Planner adds "Send Message" step, it blocks.
    # Let's try to mock generate_plan for this specific test to ensure mismatch.
    
    import Backend.Planner
    original_plan = Backend.Planner.generate_plan
    
    def mock_bad_plan(query, **kwargs):
        return {
            "plan": [
                {"action": "open", "target": "whatsapp"}, 
                {"action": "type", "target": "Spam Message"},
                {"action": "press", "target": "enter"}
            ]
        }
    
    Backend.Planner.generate_plan = mock_bad_plan
    
    gm.create_goal("Open WhatsApp")
    res = gm.execute_goal(list(gm.active_goals.keys())[-1])
    print(f"Result: {res}")
    
    if "Plan unsafe" in res or "Mismatch" in res:
        print("[PASS] Mismatch blocked execution.")
    else:
        print(f"[FAIL] Mismatch NOT blocked. Result: {res}")

    # Restore
    Backend.Planner.generate_plan = original_plan

if __name__ == "__main__":
    test_v4_loop()
