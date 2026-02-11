import json
import os
import urllib.parse
from typing import List, Tuple
from FRIDAY.core.models import Intent, AutomationAction, VerificationResult, AutomationAction as Action
from FRIDAY.layers.executors.base_executor import BaseExecutor

class YouTubeExecutor(BaseExecutor):
    def __init__(self):
        self.config_path = os.path.join(os.getcwd(), "FRIDAY", "config", "media_ui_map.json")
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            return {}
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def create_play_plan(self, intent: Intent) -> Tuple[List[AutomationAction], AutomationAction]:
        query = intent.parameters.get("query", "")
        steps = []
        
        # 1. Open Browser to Search Results
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        # We use 'run_terminal_command' to open URL with default browser
        start_cmd = f"start {url}"
        steps.append(Action(type="run_terminal_command", params={"command": start_cmd}))
        steps.append(Action(type="wait", params={"seconds": 4.0})) # Wait for load

        # 2. Click First Video
        youtube_cfg = self.config.get("youtube", {})
        if youtube_cfg.get("calibrated"):
            coords = youtube_cfg.get("first_video")
            steps.append(Action(type="click_at", params={"x": coords["x"], "y": coords["y"]}))
        else:
             # Fallback: Tab navigation? YouTube is accessible.
             # Tab approx 5-10 times gets to first video? Unreliable.
             # Better fallback: Use a specialized browser tool if available, or just hope 'AutoPlay' works?
             # For now, we rely on calibration for 100% success.
             # Partial Fallback: Click center screen? (Risky)
             pass

        # 3. Verification
        # Check window title for "YouTube"
        verification = Action(type="verify_browser_title", params={"expected_substring": "YouTube"})
        
        return steps, verification
