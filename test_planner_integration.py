from Backend.Planner import generate_plan
import json

def test_whatsapp_plan():
    print("Testing WhatsApp Plan Generation...")
    query = "send a message to brother 2 saying hello"
    plan = generate_plan(query)
    
    print(f"Query: {query}")
    print(f"Generated Plan: {json.dumps(plan, indent=2)}")
    
    # Validation
    actions = [step['action'] for step in plan.get('plan', [])]
    if "send_whatsapp" in actions:
        print("SUCCESS: Plan contains 'send_whatsapp' action.")
    else:
        print("FAILURE: Plan is missing 'send_whatsapp' action.")
        # Print actions to see what happened
        print(f"Actual Actions: {actions}")

if __name__ == "__main__":
    test_whatsapp_plan()
