import sys
import os
import time

# Ensure root is in path
sys.path.append(os.getcwd())

from FRIDAY.core.models import Intent, ActionDomain
from FRIDAY.layers.planners.code_planner import CodePlanner
from FRIDAY.layers.automation_engine import AutomationEngine

def test_backend_code():
    print("\n=== Testing Backend Code Flow with Heuristic Cleanup ===")
    
    planner = CodePlanner()
    # Simulate an intent that might trigger bad LLM output (though we can't force LLM to be bad here, 
    # we simulate the pipeline).
    intent = Intent(
        domain=ActionDomain.CODE,
        action="write_code",
        parameters={"task": "Calculate sum of digits of 12345", "language": "python"},
        original_query="Write python code to sum digits",
        confidence=1.0
    )
    
    print("[Planner] Planning...")
    # NOTE: This calls the ACTUAL LLM. If the LLM behaves well, this test passes trivially.
    # To truly test the cleaning, we'd need to mock 'generate_code' or the LLM response.
    # But running this verifies we didn't break valid generation.
    plan = planner.plan(intent)
    
    print(f"[Planner] Steps: {len(plan.steps)}")
    
    engine = AutomationEngine()
    print("[Engine] Executing...")
    result = engine.execute_plan(plan)
    
    print(f"[Result] Success: {result.success}")
    if result.success:
        print("Backend Code Execution Passed!")
    else:
        print(f"Failed: {result.error_message}")

if __name__ == "__main__":
    test_backend_code()
