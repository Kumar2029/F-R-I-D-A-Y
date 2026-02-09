from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction

class SystemPlanner:
    def plan(self, intent: Intent) -> ExecutionPlan:
        steps = []
        action = intent.action.lower()
        
        if action == "open":
            app_name = intent.parameters.get("app_name") or intent.parameters.get("name")
            steps.append(AutomationAction(type="open_app", params={"app_name": app_name}))
            
        elif action == "close":
            app_name = intent.parameters.get("app_name")
            steps.append(AutomationAction(type="close_app", params={"app_name": app_name}))
            
        elif action == "volume":
            level = intent.parameters.get("level")
            steps.append(AutomationAction(type="system_volume", params={"level": level}))

        return ExecutionPlan(intent=intent, steps=steps)
