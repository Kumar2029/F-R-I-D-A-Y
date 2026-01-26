import sys
import os

# Ensure Backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from Backend.GoalExtractor import GoalExtractor
from Backend.StrategySelector import StrategySelector
from Backend.OutcomeManager import OutcomeManager, Outcome

def test_goal_extraction():
    print("Testing Goal Extraction...")
    extractor = GoalExtractor()
    
    # Test Case 1
    input1 = "Tell Mom I'll be late"
    goal1 = extractor.extract_goal(input1)
    print(f"Input: '{input1}' -> Goal: {goal1}")
    assert goal1.goal_id == "send_message"
    assert goal1.target == "Mom"
    
    # Test Case 3 (Image Gen)
    input3 = "Friday generate me a image of flower"
    goal3 = extractor.extract_goal(input3)
    print(f"Input: '{input3}' -> Goal: {goal3}")
    assert goal3.goal_id == "generate_image"
    assert "flower" in goal3.content
    
    # Test Case 4 (Simple Gen)
    input4 = "create image of cat"
    goal4 = extractor.extract_goal(input4)
    print(f"Input: '{input4}' -> Goal: {goal4}")
    assert goal4.goal_id == "generate_image"
    
    print("Goal Extraction Passed!\n")

def test_strategy_selection():
    print("Testing Strategy Selection...")
    selector = StrategySelector()
    
    from Backend.GoalExtractor import Goal
    
    # Test Case 1: Send Message
    goal1 = Goal("send_message", target="Dad", content="Hello")
    strategy1 = selector.select_strategy(goal1)
    print(f"Goal: {goal1} -> Strategy: {strategy1}")
    assert strategy1.strategy_id == "send_whatsapp"
    
    print("Strategy Selection Passed!\n")

def test_outcome_manager():
    print("Testing Outcome Manager...")
    # Use a temp dir for test
    om = OutcomeManager(memory_dir="test_memory")
    
    outcome = Outcome("test_goal", "test_strategy", True, 1.5, 0, False)
    om.save_outcome(outcome)
    
    # Verify save
    import json
    with open("test_memory/outcomes.json", "r") as f:
        data = json.load(f)
        assert len(data) > 0
        assert data[-1]["goal_id"] == "test_goal"
    
    print("Outcome Manager Passed!\n")
    
    # Cleanup
    try:
        os.remove("test_memory/outcomes.json")
        os.rmdir("test_memory")
    except:
        pass

if __name__ == "__main__":
    test_goal_extraction()
    test_strategy_selection()
    test_outcome_manager()
    print("ALL TESTS PASSED")
