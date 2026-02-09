from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction, VerificationResult

class MediaPlanner:
    def plan(self, intent: Intent) -> ExecutionPlan:
        action = intent.action.lower()
        steps = []
        verification = None
        
        # Check Parameters first, then Hints
        platform = intent.parameters.get("platform", "").lower()
        if not platform and intent.hints and intent.hints.preferred_platform:
            platform = intent.hints.preferred_platform.lower()
        if not platform:
             platform = "spotify" # Default fallback
             
        query = intent.parameters.get("query", "")
        
        if action == "play":
            if "spotify" in platform:
                # 1. Focus App
                steps.append(AutomationAction(type="open_app", params={"app_name": "Spotify"}))
                steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))
                
                # 2. Robust Search (Clear & Type)
                steps.append(AutomationAction(type="press_key", params={"key": "ctrl+l"}))
                steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
                steps.append(AutomationAction(type="press_key", params={"key": "ctrl+a"})) # Select all
                steps.append(AutomationAction(type="press_key", params={"key": "backspace"})) # Clear
                steps.append(AutomationAction(type="type_text", params={"text": query}))
                steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
                steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
                
                # 3. Select & Play
                steps.append(AutomationAction(type="wait", params={"seconds": 1.5}))
                steps.append(AutomationAction(type="press_key", params={"key": "tab"})) # Ensure focus moves to content
                steps.append(AutomationAction(type="press_key", params={"key": "enter"})) # Play top result
                
                # 4. Verification
                steps.append(AutomationAction(type="wait", params={"seconds": 3.0})) # Wait for title update
                verification = AutomationAction(
                    type="verify_media_title", 
                    params={"expected_title": query, "app_name": "Spotify"}
                )
                
            elif "youtube" in platform:
                steps.append(AutomationAction(type="open_url", params={"url": f"https://www.youtube.com/results?search_query={query}"}))
                steps.append(AutomationAction(type="wait", params={"seconds": 3.0}))
                # Click first video?
                # Automating browser without Selenium/Playwright deeper integration is hard with just clicks.
                # Assuming 'open_url' opens the results. User might need to click?
                # User request: "Play ... on YouTube".
                # Automation Layer should handle "click_first_result".
                steps.append(AutomationAction(type="click_web_element", params={"selector": "first_video"}))
                
                verification = AutomationAction(
                    type="verify_browser_title", 
                    params={"expected_substring": query}
                )
        
        elif action == "pause" or action == "stop":
             steps.append(AutomationAction(type="media_control", params={"command": "pause"}))

        return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)
