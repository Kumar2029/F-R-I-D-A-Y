import sys
import os
import time
# Ensure root is in path
sys.path.append(os.getcwd())

from FRIDAY.core.models import Intent, ActionDomain, AutomationAction, ExecutionPlan
from FRIDAY.layers.automation_engine import AutomationEngine

def test_whatsapp():
    print("--- Testing WhatsApp Automation ---")
    
    # 1. Define the plan manually (Simulation of CommunicationPlanner)
    steps = [
        # Open
        AutomationAction(type="open_app", params={"app_name": "WhatsApp"}),
        
        # Wait for Window
        AutomationAction(type="wait_for_window", params={"title": "WhatsApp", "timeout": 20.0}),
        
        # Explicit Wait for Load
        AutomationAction(type="wait", params={"seconds": 5.0}),
        
        # Focus Attempt (Click top-leftish safe zone? Or just Tab?)
        # Let's try Tab to wake up UI
        # AutomationAction(type="press_key", params={"key": "tab"}), 
        
        # Search
        AutomationAction(type="press_key", params={"key": "ctrl+f"}),
        AutomationAction(type="wait", params={"seconds": 1.0}),
        
        # Type "Dad" (Example)
        AutomationAction(type="type_text", params={"text": "Vasanth"}),
        
        # Wait
        AutomationAction(type="wait", params={"seconds": 2.0}),
        
        # Select
        AutomationAction(type="press_key", params={"key": "enter"}),
        
        # Type Message
        AutomationAction(type="type_text", params={"text": "This is a test message from JARVIS debug."}),
    ]
    
    plan = ExecutionPlan(
        intent=Intent(ActionDomain.ACTION, "send_message", {}, "debug"),
        steps=steps
    )
    
    engine = AutomationEngine()
    result = engine.execute_plan(plan)
    
    print(f"Result: {result.success}")
    if not result.success:
        print(f"Error: {result.message}")

if __name__ == "__main__":
    test_whatsapp()
