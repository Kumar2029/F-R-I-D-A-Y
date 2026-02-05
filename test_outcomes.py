import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch
from Backend.contracts import Goal, Strategy
from Backend.outcomes import Outcome
from Backend.OutcomeVerifier import OutcomeVerifier

# Mock Automation to simulate failures
mock_automation = AsyncMock()

# Import GoalManager after patching Automation? 
# Hard to patch 'from Backend.Automation import Automation' directly in an already imported module?
# We'll use unittest.mock.patch in the test logic.

from Backend.GoalManager import GoalManager

# Setup: Clear logs
if os.path.exists("memory/failures.json"):
    os.remove("memory/failures.json")

async def test_retry_success_on_second_attempt():
    print("\n[Test] Retry Success on 2nd Attempt")
    
    # Setup mocks
    mock_outcomes = [
        [Outcome(success=False, reason="Search input not ready (focus issue)")], # Attempt 1: Transient Fail
        [Outcome(success=True)]                                                  # Attempt 2: Success
    ]
    
    with patch('Backend.GoalManager.Automation', side_effect=mock_outcomes) as mock_auto:
        with patch('Backend.GoalManager.generate_plan', return_value={"plan": [{"action": "test", "target": "foo"}]}):
            # Initialize
            gm = GoalManager()
            gm.active_goals = {"123": {"id": "123", "description": "test retry", "attempts": 0, "max_attempts": 3, "plan": [], "state": "planning"}}
            
            # Mock extraction/selection/planning parts
            gm.goal_extractor.extract_goal = MagicMock(return_value=Goal(name="test_goal", target="foo"))
            gm.strategy_selector.select_strategy = MagicMock(return_value=Strategy(name="test_strategy", confidence=0.9, reason="test"))
            
            # Execute
            result = gm.execute_goal("123")
            print(f"Result: {result}")
            
            # Verify attempts
            print(f"Automation call count: {mock_auto.call_count}")
            if mock_auto.call_count == 2:
                print("SUCCESS: Retried exactly once.")
            else:
                print(f"FAILED: Expected 2 calls, got {mock_auto.call_count}")

            if "completed successfully" in result:
                print("SUCCESS: Goal completed.")
            else:
                print("FAILED: Goal did not complete.")

async def test_fail_on_max_retries():
    print("\n[Test] Fail on Max Retries")
    
    # Setup mocks: 3 consecutive failures (Attempt 1, Retry 1, Retry 2) -> Max 2 retries = 3 total attempts
    mock_outcomes = [
        [Outcome(success=False, reason="Focus issue")], 
        [Outcome(success=False, reason="Focus issue")],
        [Outcome(success=False, reason="Focus issue")]
    ]
    
    with patch('Backend.GoalManager.Automation', side_effect=mock_outcomes) as mock_auto:
         with patch('Backend.GoalManager.generate_plan', return_value={"plan": [{"action": "test", "target": "foo"}]}):
             gm = GoalManager()
             gm.active_goals = {"456": {"id": "456", "description": "test fail", "attempts": 0, "max_attempts": 3, "plan": [], "state": "planning"}}
             
             gm.goal_extractor.extract_goal = MagicMock(return_value=Goal(name="test_goal", target="foo"))
             gm.strategy_selector.select_strategy = MagicMock(return_value=Strategy(name="test_strategy", confidence=0.9, reason="test"))
             
             result = gm.execute_goal("456")
             print(f"Result: {result}")
             
             print(f"Automation call count: {mock_auto.call_count}")
             if mock_auto.call_count == 3:
                 print("SUCCESS: Exhausted all 3 attempts.")
             else:
                 print(f"FAILED: Expected 3 calls, got {mock_auto.call_count}")

             if "failed" in result:
                 print("SUCCESS: Reported failure.")
             else:
                 print("FAILED: Did not report failure.")

async def verify_failure_log():
    print("\n[Test] Verifying Failure Log")
    log_file = "memory/failures.json"
    if os.path.exists(log_file):
        with open(log_file) as f:
            data = json.load(f)
            if len(data) > 0 and data[-1]["goal"] == "test_goal":
                print(f"SUCCESS: Failure logged: {data[-1]['reason']}")
            else:
                print("FAILED: Log entry not found or incorrect.")
    else:
        print("FAILED: Log file missing.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Patch GSOAdapter to avoid trying to parse our fake plan actions
    with patch('Backend.GoalManager.GSOAdapter.plan_to_commands', return_value=["test_cmd"]):
        loop.run_until_complete(test_retry_success_on_second_attempt())
        loop.run_until_complete(test_fail_on_max_retries())
        loop.run_until_complete(verify_failure_log())
    loop.close()
