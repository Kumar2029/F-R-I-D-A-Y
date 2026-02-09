import sys
import os
import time
import traceback

# Ensure root is in path
sys.path.append(os.getcwd())

from FRIDAY.core.models import Intent, ActionDomain
from FRIDAY.core.router import DomainRouter
from FRIDAY.layers.intent_layer import parse_intent
from FRIDAY.layers.feedback_layer import FeedbackLayer
from FRIDAY.layers.automation_engine import AutomationEngine
from FRIDAY.layers.verification_engine import VerificationEngine
from FRIDAY.layers.learning_layer import LearningAdvisoryLayer
from FRIDAY.layers.planners.media_planner import MediaPlanner
from FRIDAY.layers.planners.code_planner import CodePlanner
from FRIDAY.layers.planners.system_planner import SystemPlanner
from FRIDAY.layers.planners.general_planner import GeneralPlanner

class TextConsoleOrchestrator:
    def __init__(self):
        self.router = DomainRouter()
        self.feedback = FeedbackLayer()
        self.automation = AutomationEngine()
        self.verification = VerificationEngine()
        self.learning = LearningAdvisoryLayer()
        
        # Initialize Planner Instances
        self.planners = {
            "MediaPlanner": MediaPlanner(),
            "CodePlanner": CodePlanner(),
            "SystemPlanner": SystemPlanner(),
            "GeneralPlanner": GeneralPlanner(),
        }
        
    def process_command(self, text):
        print(f"\n[Input] Simulated: '{text}'")
        
        # 1. INTENT
        print("[Intent] Parsing...")
        intent = parse_intent(text)
        print(f"[Intent] {intent}")
        
        if intent.confidence < 0.6:
            print("[System] Low confidence. Refusing.")
            return

        # 1.5 LEARNING ADVISE
        print("[Learning] Advising...")
        intent = self.learning.advise(intent)
        print(f"[Intent+Hints] {intent}")

        # 2. ROUTER
        planner_name = self.router.route(intent)
        print(f"[Router] {planner_name}")
        planner = self.planners.get(planner_name)
        
        # 3. PLANNER
        print(f"[Planner] Generating plan...")
        plan = planner.plan(intent)
        
        for i, step in enumerate(plan.steps):
            print(f"  Step {i+1}: {step.type} {step.params}")

        # 4. AUTOMATION
        print(f"[Automation] Executing plan...")
        # We can simulate execution or actually run it. 
        # For 'write code', we might want to actually run it to see if files are created.
        result = self.automation.execute_plan(plan)
        
        if result.success:
            print("[Automation] Success.")
        else:
            print(f"[Automation] Failed: {result.message}")
            return

        # 5. VERIFICATION
        print("[Verification] Verifying...")
        verify_result = self.verification.verify(plan.verification_step)
        
        if verify_result.success:
            print(f"[Verification] Passed: {verify_result.message}")
        else:
            print(f"[Verification] Failed: {verify_result.error_message}")

        # 6. LEARNING UPDATE
        self.learning.learn(intent, plan, verify_result)

if __name__ == "__main__":
    console = TextConsoleOrchestrator()
    
    # Test Cases
    commands = [
        "Play Blinding Lights on Spotify",
        "Write a python program to print 'Hello Friday' to the console",
        "What is Artificial Intelligence?",
        "Search for SpaceX Starship launch",
        "Send a message to John saying Hello World"
    ]
    
    for cmd in commands:
        console.process_command(cmd)
        print("-" * 50)
