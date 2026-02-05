import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from Backend.contracts import Goal, Strategy
from Backend.Subgoal import Subgoal
from Backend.outcomes import Outcome
# Import GoalManager after patches? No, need to patch where it is IMPORTED.
# GoalManager imports: from Backend.Automation import Automation
# So we patch Backend.GoalManager.Automation

class TestPartialRecovery(unittest.TestCase):

    @patch('Backend.GoalManager.GoalExtractor')
    @patch('Backend.GoalManager.GoalDecomposer')
    @patch('Backend.GoalManager.StrategySelector')
    @patch('Backend.GoalManager.generate_plan')
    @patch('Backend.GoalManager.Verifier')
    @patch('Backend.GoalManager.Automation', new_callable=AsyncMock) 
    @patch('Backend.GoalManager.GSOAdapter')
    @patch('Backend.GoalManager.OutcomeManager')
    @patch('Backend.ContextEngine.ContextEngine')
    def test_partial_recovery(self, MockContext, MockOutcomeManager, MockGSO, MockAutomation, MockVerifier, MockPlan, MockStrategy, MockDecomposer, MockExtractor):
        
        # Import GoalManager here to avoid early import issues or side effects
        from Backend.GoalManager import GoalManager
        
        gm = GoalManager()
        
        # 1. Setup Goal & Decomposition
        goal_desc = "Test Recovery"
        goal_obj = Goal(name="test_goal", target="test")
        
        gm.goal_extractor.extract_goal.return_value = goal_obj
        
        # Mock Decomposer to return 2 subgoals
        sg1 = Subgoal(id="1", description="step 1")
        sg2 = Subgoal(id="2", description="step 2")
        gm.failure_analyzer = MagicMock()
        gm.failure_analyzer.analyze_failure.return_value = {
            "correction": "RETRY",
            "risk_modifier": 0.0,
            "recommendation": "RETRY",
            "failure_count": 1
        }
        
        # Mock Decomposer instance
        # GoalManager instantiates GoalDecomposer() inside execute_goal or __init__?
        # In __init__: "from Backend.GoalManager import GoalDecomposer" is NOT done. 
        # Only in execute_goal?
        # Step 1802: execute_goal has "from Backend.GoalDecomposer import GoalDecomposer" inside method? No.
        # It imports at top level in Step 1802?
        # Line 16: from Backend.GoalDecomposer import GoalDecomposer
        # Line 65: inside execute_goal... redundant import?
        # I'll rely on the patch 'Backend.GoalManager.GoalDecomposer' handling top level.
        
        mock_decomposer_instance = MockDecomposer.return_value
        mock_decomposer_instance.decompose.return_value = [sg1, sg2]

        # Mock Strategy
        strategy_safe = Strategy(name="test_strat", confidence=0.9, reason="test")
        gm.strategy_selector.select_strategy.return_value = strategy_safe
        
        # Mock Verifier
        gm.verifier.verify_plan.return_value = (True, "Reason", "verification_obj")
        MockGSO.plan_to_commands.return_value = ["cmd"]
        
        # Mock Automation Execution
        # GoalManager calls: step_outcomes = asyncio.run(Automation(commands))
        # Wait, GoalManager.py calls asyncio.run(Automation(...))?
        # If GoalManager is running in sync context, yes.
        # Line 150: step_outcomes = asyncio.run(Automation(commands))
        # So we patch Automation.
        
        outcome_success = Outcome(success=True)
        outcome_fail = Outcome(success=False, reason="Mock Failure")
        
        # Side Effects for Automation
        # Call 1: Step 1 -> Success
        # Call 2: Step 2 attempt 1 -> Failure
        # Call 3: Step 2 attempt 2 -> Success
        MockAutomation.side_effect = [
            [outcome_success],
            [outcome_fail],
            [outcome_success]
        ]
        
        try:
            # Execute
            print("Executing Goal...")
            goal_id = gm.create_goal(goal_desc)
            result = gm.execute_goal(goal_id)
            
            # Assertions
            self.assertEqual(result, "Goal Completed")
            
            # Verify Automation called 3 times
            self.assertEqual(MockAutomation.call_count, 3)
            print(f"Automation call count: {MockAutomation.call_count}")
            
            # Verify FailureAnalyzer called once
            gm.failure_analyzer.analyze_failure.assert_called_once()
            print("Failure Analyzer called successfully.")
            
            print("[Pass] Partial Recovery Verification: Step 2 failed and recovered.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

if __name__ == '__main__':
    unittest.main()
