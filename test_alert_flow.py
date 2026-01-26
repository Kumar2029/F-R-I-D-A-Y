from Backend.Model import FirstLayerDMM
from Backend.GoalManager import GoalManager
from unittest.mock import MagicMock

# Mock GoalManager to simulate failure
def mock_execute_goal(goal_id):
    return "Failed: Multiple failures detected. Recommendation: ASK_USER"

# Apply mock
GoalManager.execute_goal = MagicMock(side_effect=mock_execute_goal)

print("Testing Alert Flow...")
response = FirstLayerDMM("make me a sandwich")
print(f"Response: {response}")

if response[0].startswith("alert"):
    print("SUCCESS: Model correctly returned 'alert' command.")
else:
    print(f"FAILURE: Model returned '{response[0]}', expected 'alert ...'")
