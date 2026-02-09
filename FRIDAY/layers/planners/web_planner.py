from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction

class WebPlanner:
    def plan(self, intent: Intent) -> ExecutionPlan:
        steps = []
        action = intent.action.lower()
        query = intent.parameters.get("query", "")
        
        if not query:
            return ExecutionPlan(intent=intent, steps=[])

        # Constitution: SEARCH is Read-Only / Information Gathering. 
        # "NO execution".
        # So we just open the search results.
        
        # 1. Open Browser (Chrome/Edge)
        # 2. Type URL or Search
        
        # Simpler: Use 'start https://google.com/search?q=...' via terminal? 
        # But we must use Automation Primitives if possible.
        # Let's use "open_app" -> "Chrome" -> "Type URL".
        
        steps.append(AutomationAction(type="open_app", params={"app_name": "Google Chrome"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))
        
        # Focus Address Bar (Alt+D or Ctrl+L)
        steps.append(AutomationAction(type="press_key", params={"key": "alt+d"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
        
        # Type Search URL
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        steps.append(AutomationAction(type="type_text", params={"text": search_url}))
        steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
        steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
        
        # Verification
        # Check window title contains query
        verification = AutomationAction(
             type="verify_browser_title",
             params={"expected_substring": query}
        )
        
        return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)
