import asyncio
import os
import json
from unittest.mock import MagicMock, patch, AsyncMock
from Backend.contracts import Goal
from Backend.Subgoal import Subgoal
from Backend.GoalDecomposer import GoalDecomposer
from Backend.GoalManager import GoalManager
from Backend.outcomes import Outcome

HEALTH_FILE = "memory/strategy_health.json"
FAILURES_FILE = "memory/failures.json"

def setup_clean_state():
    if os.path.exists(HEALTH_FILE): os.remove(HEALTH_FILE)
    if os.path.exists(FAILURES_FILE): os.remove(FAILURES_FILE)
    print("\n[Setup] Cleaned memory.")

def test_decomposition():
    print("\n[Test] Goal Decomposition Rules")
    decomposer = GoalDecomposer()
    
    # Test send_message
    goal = Goal(name="send_message", target="Mom")
    subgoals = decomposer.decompose(goal)
    descriptions = [s.description for s in subgoals]
    print(f"Subgoals for send_message: {descriptions}")
    
    expected = ["open WhatsApp", "focus search bar", "type Mom", "press enter"] # Simplified list
    # Actual list may vary based on implementation. Check subsets.
    if "open WhatsApp" in descriptions and "type Mom" in descriptions:
        print("SUCCESS: Decomposition looks correct.")
    else:
        print("FAILED: Decomposition missing steps.")

async def test_subgoal_execution_and_correction():
    print("\n[Test] Subgoal Execution & Self-Correction")
    setup_clean_state()
    
    # Mock Automation to simulate failure on 2nd attempt of a step
    # We want to fail "focus search bar" once, then succeed.
    
    # We need to control Automation output based on command inputs?
    # Hard to map exact command strings here without knowing Adapter output.
    # But we can side_effect a sequence of outcomes.
    # Total steps for send_message: 4.
    # Step 1: Success
    # Step 2: Fail (Reason: Focus lost) -> Correction: REFOCUS -> Retry -> Success
    # Step 3: Success
    # Step 4: Success
    
    # Flattened outcome sequence:
    # 1. [Success] (Step 1)
    # 2. [Fail]    (Step 2 - Try 1)
    # 3. [Success] (Step 2 - Try 2)
    # 4. [Success] (Step 3)
    # 5. [Success] (Step 4)
    
    mock_outcomes = [
        [Outcome(success=True)],       
        [Outcome(success=False, reason="Input field not active (Focus lost)")],
        [Outcome(success=True)],
        [Outcome(success=True)],
        [Outcome(success=True)]
    ]
    
    # Mock dependencies
    with patch('Backend.GoalManager.Automation', side_effect=mock_outcomes) as mock_auto:
        with patch('Backend.GoalManager.generate_plan', return_value={"plan": [{"action": "mock", "target": "mock"}]}):
             with patch('Backend.GoalManager.GSOAdapter.plan_to_commands', return_value=["mock_cmd"]):
                gm = GoalManager()
                
                # Setup goal
                goal_id = gm.create_goal("send message to Mom")
                # Mock GoalExtractor to return semantic goal
                gm.goal_extractor.extract_goal = MagicMock(return_value=Goal(name="send_message", target="Mom"))
                
                # Mock StrategySelector to return high confidence
                gm.strategy_selector.select_strategy = MagicMock(return_value=MagicMock(name="mock_strat", confidence=0.9))
                # Strategy object must have .name
                gm.strategy_selector.select_strategy.return_value.name = "mock_strategy"
                gm.strategy_selector.select_strategy.return_value.confidence = 0.9
                
                # Mock Verifier to always pass
                gm.verifier.verify_plan = MagicMock(return_value=(True, 0, [{"action": "mock_cmd"}]))

                # Execute
                result = gm.execute_goal(goal_id)
                print(f"Goal Result: {result}")
                
                # Verify Logic
                # Expect 5 calls to Automation (1 + 2 + 1 + 1)
                print(f"Automation Calls: {mock_auto.call_count}")
                
                if mock_auto.call_count == 5 and "Completed" in result:
                    print("SUCCESS: Partial failure recovered via self-correction.")
                else:
                    print(f"FAILED: Expected 5 calls, got {mock_auto.call_count}. Result: {result}")

if __name__ == "__main__":
    test_decomposition()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_subgoal_execution_and_correction())
    loop.close()
