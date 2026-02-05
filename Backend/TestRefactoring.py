import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path to import Backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Backend.contracts import Goal
from Backend.StrategyHealth import StrategyHealth, StrategyHealthManager

class TestRefactoring(unittest.TestCase):

    def test_strategy_health_logic(self):
        try:
            """Part 4: Standardize StrategyHealth Class"""
            health = StrategyHealth()
            
            # Initial State
            self.assertEqual(health.score, 1.0, "Initial score should be 1.0 (Optimistic)")
            self.assertEqual(health.failure_count, 0)
            
            # Record Success
            health.success_count += 1
            health.failure_count = 0
            self.assertEqual(health.score, 1.0, "Score should remain 1.0 after success with no failures")
            
            # Record Failure
            health.failure_count = 1
            # In our logic, we calculate score dynamicall: success / (success + failure)
            # 1 / (1 + 1) = 0.5
            self.assertEqual(health.score, 0.5, "Score should be 0.5 after 1 success and 1 failure")
            
            health.success_count += 1
            health.failure_count = 0 # Explicitly clear failure_count to match logic
            self.assertEqual(health.score, 1.0, "Score should be 1.0 after success with reset failures")
            print("test_strategy_health_logic PASSED")
        except Exception as e:
            print(f"test_strategy_health_logic FAILED: {e}")
            raise e

    @patch('Backend.GoalManager.ContentWriterAI')
    @patch('Backend.GoalManager.TTS')
    def test_content_bypass(self, mock_tts, mock_content_ai):
        try:
            """Part 2: Content Goals Bypass Automation"""
            from Backend.GoalManager import GoalManager
            
            gm = GoalManager()
            mock_content_ai.return_value = "Generated Content"
            
            # Create a content goal
            goal_desc = "tell me a story about AI"
            
            # Mocking GoalExtractor for simplicity or reliance on real one?
            # let's mock extract_goal to return a Goal object
            with patch.object(gm.goal_extractor, 'extract_goal') as mock_extract:
                mock_extract.return_value = Goal(name="story", content="AI", target=None)
                
                # Create goal record manually to bypass create_goal UUID gen if needed, or just usage
                goal_id = gm.create_goal(goal_desc)
                
                result = gm.execute_goal(goal_id)
                
                self.assertIn("Content Bypass", result)
                mock_content_ai.assert_called_with("AI")
                mock_tts.assert_called_with("Generated Content")
            print("test_content_bypass PASSED")
        except Exception as e:
             print(f"test_content_bypass FAILED: {e}")
             raise e

    @patch('Backend.GoalManager.TTS')
    def test_whatsapp_defaults(self, mock_tts):
        try:
            """Part 5: WhatsApp Safety Defaults"""
            from Backend.GoalManager import GoalManager
            gm = GoalManager()
            
            with patch.object(gm.goal_extractor, 'extract_goal') as mock_extract:
                # Case 1: Mom -> Hi
                mock_extract.return_value = Goal(name="send_whatsapp", target="Mom", content=None)
                gm.create_goal("message mom")
                gm.execute_goal(list(gm.active_goals.keys())[-1])
                
                # Verify the GOAL object was modified in place? 
                # execute_goal gets 'derived_goal' from extractor.
                # We need to verify that derived_goal.content was updated.
                # Since we mocked extract_goal to return a specific object, we can check that object.
                self.assertEqual(mock_extract.return_value.content, "Hi")
                
                # Case 2: Brother -> Hey
                mock_extract.return_value = Goal(name="send_whatsapp", target="Brother", content=None)
                gm.execute_goal(list(gm.active_goals.keys())[-1])
                self.assertEqual(mock_extract.return_value.content, "Hey")
            print("test_whatsapp_defaults PASSED")
        except Exception as e:
            print(f"test_whatsapp_defaults FAILED: {e}")
            raise e

if __name__ == '__main__':
    unittest.main()
