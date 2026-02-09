from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction
from dotenv import dotenv_values

class CommunicationPlanner:
    def plan(self, intent: Intent) -> ExecutionPlan:
        steps = []
        action = intent.action.lower()
        
        # WhatsApp Logic
        if "whatsapp" in action or "message" in action:
             # Basic WhatsApp Web Automation or usage of 'pywhatkit' if allowed?
             # User mentioned "Automation is UI-based".
             # Strict flow: Open WhatsApp -> Search Contact -> Type Message -> Send
             
             contact = intent.parameters.get("contact", "")
             message = intent.parameters.get("message", "")
             
             if not contact or not message:
                 # Incomplete intent
                 return ExecutionPlan(intent=intent, steps=[])

             steps.append(AutomationAction(type="open_app", params={"app_name": "WhatsApp"}))
             steps.append(AutomationAction(type="wait", params={"seconds": 3.0}))
             
             # Search Contact (Ctrl+F or Click search)
             # WhatsApp Desktop (Windows app) shortcuts:
             # Ctrl+F: Search
             steps.append(AutomationAction(type="press_key", params={"key": "ctrl+f"}))
             steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
             steps.append(AutomationAction(type="type_text", params={"text": contact}))
             steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
             steps.append(AutomationAction(type="press_key", params={"key": "enter"})) # Select contact
             steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
             
             # Type Message
             steps.append(AutomationAction(type="type_text", params={"text": message}))
             steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
             
             # Send
             steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
             
             # Verification
             # Check if message bubble exists? Hard without OCR.
             # Check "sent" tick? Hard.
             # We can verify the contact name is in the window title.
             verification = AutomationAction(
                 type="verify_window_title",
                 params={"expected_substring": contact}
             )
             
             return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)

        return ExecutionPlan(intent=intent, steps=[])
