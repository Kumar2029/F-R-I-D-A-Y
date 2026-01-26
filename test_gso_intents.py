
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

from Backend.GoalExtractor import GoalExtractor
from Backend.StrategySelector import StrategySelector
from Backend.Planner import generate_plan
from Backend.CommandCompiler import compile_commands

# Mock classes for testing
class MockModel:
    def __init__(self):
        pass


async def test_messaging_intent():
    print("\n--- Testing Messaging Intent ---")
    query = "Send a hi message to brother 2"
    print(f"Query: {query}")

    # 1. Goal Extraction
    # Fixed: GoalExtractor does not take arguments
    extractor = GoalExtractor()
    goal = extractor.extract_goal(query)
    print(f"Goal Extracted: {goal}")
    
    if not goal or goal.goal_id != "send_message":
        print("FAILED: Incorrect goal extracted.")
        return

    # 2. Strategy Selection
    selector = StrategySelector()
    strategy = selector.select_strategy(goal)
    print(f"Strategy Selected: {strategy}")

    if not strategy or strategy.strategy_id != "send_whatsapp":
        print("FAILED: Incorrect strategy selected.")
        return

    # 3. Planning
    
    try:
        # Fixed: generate_plan signature usage
        # generate_plan(user_query, goal_obj=goal, strategy_obj=strategy)
        plan_response = generate_plan(query, goal_obj=goal, strategy_obj=strategy)
        print(f"Plan Generated: {plan_response}")
        
        # Planner returns a dict like {"plan": [...], "success_criteria": ...} or a list (v2 compat)
        if isinstance(plan_response, dict) and "plan" in plan_response:
             plan_steps = plan_response["plan"]
        elif isinstance(plan_response, list):
             plan_steps = plan_response
        else:
             print(f"FAILED: Unexpected plan format: {plan_response}")
             return

        # 4. Command Compilation
        
        # Convert plan steps to string commands if they are dictionaries
        # Expected format from Planner is [{"action": "...", "target": "..."}]
        
        commands_for_compiler = []
        for step in plan_steps:
             if isinstance(step, dict):
                 # simplistic serialization to check if logical flow holds
                 if step.get("action") == "send_whatsapp":
                      print("SUCCESS: Planner produced send_whatsapp action.")
                 else:
                      print(f"FAILED: Planner produced {step.get('action')} instead of send_whatsapp")
                      
                 cmd_str = f"{step.get('action')} {step.get('target')}"
                 commands_for_compiler.append(cmd_str)
             else:
                 commands_for_compiler.append(str(step))

        # Test Compile
        try:
            compile_commands(commands_for_compiler)
            print("SUCCESS: Commands compiled successfully")
        except Exception as e:
            print(f"FAILED: Command compilation/validation failed: {e}")

    except Exception as e:
        print(f"Planner Execution/Error: {e}")

async def test_generic_messaging_intent():
    print("\n--- Testing Generic Messaging Intent ('Send a message to Mom') ---")
    query = "Send a message to Mom"
    print(f"Query: {query}")

    extractor = GoalExtractor()
    goal = extractor.extract_goal(query)
    print(f"Goal Extracted: {goal}")
    
    if goal and goal.goal_id == "send_message" and goal.content is None:
        print("SUCCESS: Correctly identified generic intent with NO content.")
    else:
        print(f"FAILED: Goal={goal} (Expected content=None)")

async def test_search_intent():
    print("\n--- Testing Search Intent ---")
    query = "Friday search for Python Programming courses"
    print(f"Query: {query}")

    # 1. Goal Extraction
    extractor = GoalExtractor()
    goal = extractor.extract_goal(query)
    print(f"Goal Extracted: {goal}")
    
    if not goal or goal.goal_id != "search_web":
        print(f"FAILED: Incorrect goal extracted: {goal}") # Fixed printing
        # Don't return, let's see what happens.
    
    # ... rest ...
    # 2. Strategy Selection
    selector = StrategySelector()
    strategy = selector.select_strategy(goal)
    print(f"Strategy Selected: {strategy}")

    if not strategy or strategy.strategy_id != "search_web":
        print("FAILED: Incorrect strategy selected.")
        return
        
    # 3. Planner
    try:
         plan_response = generate_plan(query, goal_obj=goal, strategy_obj=strategy)
         print(f"Plan: {plan_response}")
         
         # Validation logic same as above
         if isinstance(plan_response, dict):
             steps = plan_response.get("plan", [])
         else:
             steps = plan_response
             
         if not steps:
             print("FAILED: No steps in plan")
             return
             
         first_step = steps[0]
         if first_step.get("action") == "search_web":
             print("SUCCESS: Planner produced search_web action")
         else:
             print(f"FAILED: Planner produced {first_step.get('action')}")

         # 4. Verification
         # Mock compile call
         from Backend.CommandCompiler import compile_command
         cmd = f"{first_step.get('action')} {first_step.get('target')}"
         try:
             res = compile_command(cmd)
             print(f"SUCCESS: Compiled to {res}")
         except Exception as e:
             print(f"FAILED: Compilation error {e}")

    except Exception as e:
         print(f"Planner Error: {e}")


async def test_punctuation_normalization():
    print("\n--- Testing Punctuation Normalization ---")
    
    # Case 1: Trailing punctuation in contact
    query1 = "Send a hi message to brother 2."
    print(f"Query 1: {query1}")
    extractor = GoalExtractor()
    goal1 = extractor.extract_goal(query1)
    print(f"Goal 1: {goal1}")
    
    if goal1 and goal1.target == "brother 2":
        print("SUCCESS: Removed trailing punctuation from contact.")
    else:
        print(f"FAILED: Contact not normalized. Got '{goal1.target if goal1 else None}'")

    # Case 2: Trailing punctuation in search
    query2 = "Search for python courses."
    print(f"Query 2: {query2}")
    goal2 = extractor.extract_goal(query2)
    print(f"Goal 2: {goal2}")
    
    if goal2 and goal2.target == "python courses":
        print("SUCCESS: Removed trailing punctuation from search target.")
    else:
        print(f"FAILED: Search target not normalized. Got '{goal2.target if goal2 else None}'")


if __name__ == "__main__":
    load_dotenv()
    # asyncio.run(test_messaging_intent())
    # asyncio.run(test_generic_messaging_intent())
    # asyncio.run(test_search_intent())
    asyncio.run(test_punctuation_normalization())
