from Backend.GoalExtractor import GoalExtractor
from Backend.StrategySelector import StrategySelector
from Backend.contracts import Goal
from unittest.mock import MagicMock

def test():
    print("--- START TESTS ---")
    extractor = GoalExtractor()
    
    # Test 1
    g = extractor.extract_goal("send message to mum")
    print(f"Goal 1: {g}")
    if g.content == "Hi" and g.target == "mum":
        print("PASS: Mum->Hi")
    else:
        print(f"FAIL: Mum->{g.content}")

    # Test 2
    g = extractor.extract_goal("whatsapp brother")
    print(f"Goal 2: {g}")
    if g.content == "Hey":
        print("PASS: Bro->Hey")
    else:
        print(f"FAIL: Bro->{g.content}")
        
    # Test 3: Strategy Unfreeze
    selector = StrategySelector()
    selector.health_manager = MagicMock()
    
    mh = MagicMock()
    mh.score = 0.1
    mh.failures = 1
    selector.health_manager.get_health.return_value = mh
    
    goal = Goal(name="search_web", target="test")
    s = selector.select_strategy(goal)
    print(f"Strat 1 (Fail<3): {s.name}")
    if s.name == "search_web":
        print("PASS: Unfreeze Success")
    else:
        print("FAIL: Still frozen")
        
    # Test 4: Strategy Block
    mh.failures = 4
    s2 = selector.select_strategy(goal)
    print(f"Strat 2 (Fail>=3): {s2.name}")
    if s2.name == "ask_user":
        print("PASS: Blocking Success")
    else:
        print("FAIL: Should block")

if __name__ == "__main__":
    test()
