from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction
from dotenv import dotenv_values

class CommunicationPlanner:
    def __init__(self):
        from FRIDAY.layers.contact_resolver import ContactResolver
        self.resolver = ContactResolver()

    def plan(self, intent: Intent) -> ExecutionPlan:
        steps = []
        action = intent.action.lower()
        
        # WhatsApp Logic
        if "whatsapp" in action or "message" in action:
             # robust parameter extraction
             raw_contact = (
                 intent.parameters.get("contact") or 
                 intent.parameters.get("recipient") or 
                 intent.parameters.get("person") or 
                 intent.parameters.get("to") or 
                 ""
             )
             
             message = (
                 intent.parameters.get("message") or 
                 intent.parameters.get("content") or 
                 "Hello"
             )
             
             # GUARD: Parameter missing
             if not raw_contact:
                 print("[CommunicationPlanner] Missing contact. Aborting.")
                 return ExecutionPlan(intent=intent, steps=[])

             # RESOLVE CONTACT
             contact = self.resolver.resolve(raw_contact)
             print(f"[CommunicationPlanner] Resolved '{raw_contact}' to '{contact}'")

             # --- ROBUST AUTOMATION STEPS ---
             # 1. Open App
             steps.append(AutomationAction(type="open_app", params={"app_name": "WhatsApp"}))
             
             # 2. Wait for Window (Crucial for robustness)
             steps.append(AutomationAction(type="wait_for_window", params={"title": "WhatsApp", "timeout": 15.0}))
             
             # 3. Wait for App to be Ready (Loading text to disappear)
             steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))

             # 4. Search Contact (Ctrl+F or Click search)
             # Focus Search
             steps.append(AutomationAction(type="press_key", params={"key": "ctrl+f"}))
             steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
             
             # Type Name
             steps.append(AutomationAction(type="type_text", params={"text": contact}))
             
             # 5. Wait for Search Results (UI Stability)
             steps.append(AutomationAction(type="wait_for_ui_stable", params={"duration": 1.0, "timeout": 5.0}))
             
             # 6. Select Contact (Enter)
             steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
             steps.append(AutomationAction(type="wait", params={"seconds": 1.0})) # Chat load
             
             # 7. Type Message
             steps.append(AutomationAction(type="type_text", params={"text": message}))
             
             # 8. Send
             steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
             
             # Verification: Just check window is still active/focused
             verification = AutomationAction(
                 type="verify_active_window",
                 params={"app_name": "WhatsApp"}
             )
             
             # Feedback
             steps.append(AutomationAction(type="speak", params={"text": f"Message sent to {contact}."}))
             
             return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)

        return ExecutionPlan(intent=intent, steps=[])
