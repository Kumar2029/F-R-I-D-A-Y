from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction, VerificationResult
from FRIDAY.layers.handlers.spotify_handler import SpotifyHandler

class MediaPlanner:
    def __init__(self):
        self.spotify_handler = SpotifyHandler()

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
                # DELEGATION: Using SpotifyHandler for strict 5-Phase Execution
                steps = self.spotify_handler.play_song(query)

                # 4. Verification (Strict: Process Foreground)
                verification = AutomationAction(
                    type="verify_active_window", 
                    params={"app_name": "Spotify"}
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
