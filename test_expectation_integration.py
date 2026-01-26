
import sys
import os

# Ensure we can import Backend modules
sys.path.append(os.getcwd())

# from rich import print # Disable rich to check output
import builtins
def print(*args, **kwargs):
    builtins.print(*args, **kwargs)
    sys.stdout.flush()

from Backend.Verifier import Verifier


def test_integration():
    verifier = Verifier()
    
    print("\n--- TEST 1: Matching Expectation (Safe) ---")
    query = "Open Calculator"
    plan = [{"action": "open", "target": "calculator", "risk_score": 0.1}]
    
    is_safe, risk, _ = verifier.verify_plan(plan, user_query=query)
    print(f"Query: '{query}' | Plan: {[s['action'] for s in plan]}")
    print(f"Result Risk: {risk} (Expected < 0.5)")
    if risk < 0.5:
        print("[PASS] Risk remains low for matching expectation.")
    else:
        print("[FAIL] Risk unnecessarily high.")

    print("\n--- TEST 2: Expectation Mismatch (Unsafe) ---")
    # User asks to OPEN, but Plan tries to SEND (High Scope action)
    query = "Open WhatsApp" 
    plan = [
        {"action": "open", "target": "whatsapp"},
        {"action": "type", "target": "Hello"}, # 'type' is allowed in medium/high, check ExpectationModel logic.
        # Wait, "Open" -> Low Scope -> Allowed: [open, close, wait, system]
        # 'type' is NOT allowed in Low Scope.
    ] 
    
    is_safe, risk, _ = verifier.verify_plan(plan, user_query=query)
    print(f"Query: '{query}' | Plan: {[s['action'] for s in plan]}")
    print(f"Result Risk: {risk} (Expected >= 0.5 increment)")
    
    if risk >= 0.5: # Base 0.1 + 0.5 mismatch
        print("[PASS] Expectation Mismatch detected correctly.")
    else:
        print("[FAIL] Mismatch NOT detected.")

    print("\n--- TEST 3: High Scope Query (Safe) ---")
    query = "Send a message to John"
    plan = [
        {"action": "open", "target": "whatsapp"},
        {"action": "type", "target": "Hello John"},
        {"action": "press", "target": "enter"}
    ]
    # "Send" -> High Scope -> Allowed: All actions
    
    is_safe, risk, _ = verifier.verify_plan(plan, user_query=query)
    print(f"Query: '{query}' | Plan: {[s['action'] for s in plan]}")
    print(f"Result Risk: {risk}")
    
    if risk < 0.6:
        print("[PASS] High scope query allows complex actions.")
    else:
        print("[FAIL] High scope query flagged as unsafe.")

if __name__ == "__main__":
    test_integration()
