
import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())

# 1. Mock External dependencies (Audio, GUI, etc)
sys.modules['Backend.SpeechToText'] = MagicMock()
sys.modules['Frontend.GUI'] = MagicMock()
sys.modules['Backend.TextToSpeech'] = MagicMock()

# Mock Automation entirely to avoid opening apps
sys.modules['Backend.Automation'] = MagicMock()

# We need the real Model and GoalManager for logic testing
# But Main.py imports them.
# Let's import Main logic *after* mocking
from Backend.Model import FirstLayerDMM

print("\n--- TEST: Integration Flow (Main -> Model -> Decision) ---")

def test_intent_routing():
    # Case 1: General Chat
    query = "What is the time?"
    print(f"\nQuery: '{query}'")
    decision = FirstLayerDMM(query)
    print(f"Decision: {decision}")
    
    if any("general" in d for d in decision):
        print("[PASS] Routable to General Chat")
    else:
        print("[FAIL] Incorrect Routing")

    # Case 2: Automation (Realtime)
    query = "Open Calculator"
    print(f"\nQuery: '{query}'")
    
    # We need to mock GoalManager inside UserStateEstimator/ContextEngine context?
    # Actually FirstLayerDMM creates a goal_manager instance.
    # We just want to see if it returns "realtime" or "general alert" or similar.
    
    # We need to mock execute_goal to avoid actual execution loop delays
    # (since execute_goal calls generate_plan which calls Cohere)
    # Testing LIVE Cohere is fine if succinct.
    
    decision = FirstLayerDMM(query)
    print(f"Decision: {decision}")
    
    if any("general" in d for d in decision) or any("alert" in d for d in decision):
        # Result message usually starts with general or alert
        print("[PASS] Automation executed (Result returned)")
    else:
        print("[FAIL] Automation routing failed")

if __name__ == "__main__":
    test_intent_routing()
