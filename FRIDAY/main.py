import sys
import os
import time
import traceback

# Ensure root is in path
sys.path.append(os.getcwd())

from FRIDAY.core.models import Intent, ActionDomain
from FRIDAY.core.router import DomainRouter
from FRIDAY.layers.input_layer import get_user_input
from FRIDAY.layers.intent_layer import parse_intent
from FRIDAY.layers.feedback_layer import FeedbackLayer
from FRIDAY.layers.automation_engine import AutomationEngine
from FRIDAY.layers.verification_engine import VerificationEngine
from FRIDAY.layers.learning_layer import LearningAdvisoryLayer

# Import Planners
from FRIDAY.layers.planners.media_planner import MediaPlanner
from FRIDAY.layers.planners.code_planner import CodePlanner
from FRIDAY.layers.planners.system_planner import SystemPlanner
from FRIDAY.layers.planners.general_planner import GeneralPlanner
from FRIDAY.layers.planners.communication_planner import CommunicationPlanner
from FRIDAY.layers.planners.web_planner import WebPlanner

from FRIDAY.core.ui_interface import UIInterface

class FridayOrchestrator:
    def __init__(self, ui: UIInterface = None):
        self.ui = ui
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
            "CommunicationPlanner": CommunicationPlanner(),
            "WebPlanner": WebPlanner(),
            # Add others as needed
        }
        
        self.running = True

    def start(self):
        self.feedback.speak("FRIDAY System Online. Waiting for command.")
        print("[System] FRIDAY Online.")
        
        while self.running:
            try:
                # 1. INPUT LAYER
                print("\n[Input] Listening...")
                text = get_user_input()
                if not text:
                    continue
                    
                print(f"[Input] Heard: {text}")
                if self.ui: self.ui.on_user_input(text)
                
                if "exit system" in text.lower():
                    self.feedback.speak("Shutting down.")
                    self.running = False
                    break

                # 2. INTENT LAYER
                print("[Intent] Parsing...")
                intent = parse_intent(text)
                
                if intent.confidence < 0.6:
                    self.feedback.speak("I'm not sure what you mean. Could you clarify?")
                    continue
                    
                if intent.action == "unknown" or intent.action == "error":
                    self.feedback.speak("I couldn't understand that command.")
                    continue
                
                # 2.5 LEARNING ADVISORY LAYER
                print("[Learning] Advising...")
                intent = self.learning.advise(intent)
                
                print(f"[Intent] {intent}")

                # 3. DOMAIN ROUTING LAYER
                planner_name = self.router.route(intent)
                planner = self.planners.get(planner_name)
                
                if not planner:
                    self.feedback.speak(f"I don't have a planner for {intent.domain.name} yet.")
                    continue

                # 4. PLANNER LAYER
                print(f"[Planner] Generating plan using {planner_name}...")
                plan = planner.plan(intent)
                
                if not plan.steps:
                    self.feedback.speak("I couldn't generate a plan for that.")
                    continue
                    
                print(f"[Plan] {len(plan.steps)} steps generated.")

                # 5. AUTOMATION LAYER
                msg = f"Executing {intent.action} for {intent.domain.name}."
                self.feedback.speak(msg)
                if self.ui: self.ui.on_status_change(msg)
                if self.ui: self.ui.on_assistant_output(msg)
                
                result = self.automation.execute_plan(plan)
                
                if not result.success:
                    self.feedback.speak_error(result.message)
                    continue

                # 6. VERIFICATION LAYER
                print("[Verification] Verifying outcome...")
                verify_result = self.verification.verify(plan.verification_step)
                
                if verify_result.success:
                    print("[Success] Verification Passed.")
                    self.feedback.speak("Done.")
                else:
                    print(f"[Failure] Verification Failed: {verify_result.error_message}")
                    self.feedback.speak(f"Task completed, but verification failed: {verify_result.error_message}")
                    if self.ui: self.ui.on_status_change(f"Verification Failed: {verify_result.message}")


                # 7. FEEDBACK TO LEARNING
                self.learning.learn(intent, plan, verify_result)

            except KeyboardInterrupt:
                print("\n[System] Interrupted.")
                self.running = False
            except Exception as e:
                print(f"[System] Critical Error: {e}")
                traceback.print_exc()
                self.feedback.speak("A critical system error occurred.")

if __name__ == "__main__":
    friday = FridayOrchestrator()
    friday.start()
