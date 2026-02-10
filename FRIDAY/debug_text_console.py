import sys
import os
import time
import traceback

# Ensure root is in path
sys.path.append(os.getcwd())

from FRIDAY.core.models import Intent, ActionDomain, ActionResult
from FRIDAY.core.router import DomainRouter
from FRIDAY.layers.intent_layer import parse_intent
from FRIDAY.layers.feedback_layer import FeedbackLayer
from FRIDAY.layers.automation_engine import AutomationEngine
from FRIDAY.core.models import ActionResult
from FRIDAY.layers.verification_engine import VerificationEngine
from FRIDAY.layers.learning_layer import LearningAdvisoryLayer
from FRIDAY.layers.planners.media_planner import MediaPlanner
from FRIDAY.layers.planners.code_planner import CodePlanner
from FRIDAY.layers.planners.action_planner import ActionPlanner
from FRIDAY.layers.planners.action_planner import ActionPlanner
from FRIDAY.layers.planners.general_planner import GeneralPlanner
from FRIDAY.layers.planners.communication_planner import CommunicationPlanner

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
            "ActionPlanner": ActionPlanner(),
            "CommunicationPlanner": CommunicationPlanner(),
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
        # 6. LEARNING UPDATE (Fix: Wrap in ActionResult)
        final_result = ActionResult(
            success=(result.success and verify_result.success),
            message=result.message if result.success else result.message,
            verification=verify_result,
            logs=[str(verify_result.data)] if verify_result.data else []
        )
        self.learning.learn(intent, plan, final_result)

if __name__ == "__main__":
    console = TextConsoleOrchestrator()
    
    # Test Cases
    commands = [
        "Play Blinding Lights on Spotify",
        # "Write a python program to print 'Hello Verified' to the console",
        # "Open Calculator",
        # "Send a message to Mom",  
        # "Send a message to Mom",  
        # "Send a message to John saying Hello World"
    ]
    
    for cmd in commands:
        console.process_command(cmd)
        print("-" * 50)
