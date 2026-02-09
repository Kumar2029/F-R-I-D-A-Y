import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from FRIDAY.layers.intent_layer import parse_intent
from FRIDAY.core.router import DomainRouter
from FRIDAY.core.models import Intent, ActionDomain

router = DomainRouter()

test_cases = [
    "Play Blinding Lights on Spotify",
    "Write a python program to print a triangle",
    "Open Chrome and search for news",
    "Set volume to 50%"
]

print("--- STARTING CORE VERIFICATION ---")

for text in test_cases:
    print(f"\n[Test] Input: '{text}'")
    try:
        intent = parse_intent(text)
        print(f"[Intent] {intent}")
        
        # Check if intent is valid object
        if not isinstance(intent, Intent):
             print(f"[Error] parse_intent returned {type(intent)}")
             continue

        if intent.action == "unknown" or intent.action == "error":
             print(f"[Router] Skipping due to invalid intent: {intent.action}")
             continue
             
        planner_name = router.route(intent)
        print(f"[Router] Mapped to: {planner_name}")
        
    except Exception as e:
        print(f"[Error] {e}")
        import traceback
        traceback.print_exc()

print("\n--- VERIFICATION COMPLETE ---")
