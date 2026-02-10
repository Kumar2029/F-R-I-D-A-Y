from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction

class ActionPlanner:
    def plan(self, intent: Intent) -> ExecutionPlan:
        steps = []
        action = intent.action.lower()
        
        if action == "open":
            app_name = intent.parameters.get("app_name") or intent.parameters.get("name")
            steps.append(AutomationAction(type="open_app", params={"app_name": app_name}))
            # Implicit verification via open_app primitive or we add strict verification?
            # User said "open_app must be handled ONLY by ActionPlanner".
            # We can add active window verification here too.
            steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))
            verification = AutomationAction(type="verify_active_window", params={"app_name": app_name})
            return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)
            
        elif action == "close":
            app_name = intent.parameters.get("app_name")
            steps.append(AutomationAction(type="close_app", params={"app_name": app_name}))
            
        elif action == "volume":
            level = intent.parameters.get("level")
            steps.append(AutomationAction(type="system_volume", params={"level": level}))

        return ExecutionPlan(intent=intent, steps=steps)
