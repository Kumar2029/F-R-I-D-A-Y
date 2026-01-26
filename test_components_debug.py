
import sys
import os
from dotenv import dotenv_values

# Add path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_chatbot():
    print("Testing ChatBot (Groq)...")
    try:
        from Backend.Chatbot import ChatBot
        response = ChatBot("Hello, are you working?")
        print(f"ChatBot Response: {response}")
        return True
    except Exception as e:
        print(f"ChatBot Failed: {e}")
        return False

def test_planner():
    print("\nTesting Planner (Cohere)...")
    try:
        from Backend.Planner import generate_plan
        plan = generate_plan("open notepad")
        print(f"Planner Result: {plan}")
        if plan:
            return True
        return False
    except Exception as e:
        print(f"Planner Failed: {e}")
        return False

if __name__ == "__main__":
    c = test_chatbot()
    p = test_planner()
    
    if c and p:
        print("\nAll systems operational.")
    else:
        print("\nSome systems failed.")
