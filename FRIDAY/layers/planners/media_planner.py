import os
import json
from enum import Enum
from typing import List, Optional
from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction, VerificationResult
from FRIDAY.layers.learning_layer import LearningAdvisoryLayer
from FRIDAY.layers.executors.spotify_executor import SpotifyExecutor
from FRIDAY.layers.executors.youtube_executor import YouTubeExecutor
from FRIDAY.layers.executors.local_executor import LocalExecutor

class MediaPlatform(Enum):
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    LOCAL = "local"

class MediaPlanner:
    def __init__(self):
        self.learning_layer = LearningAdvisoryLayer()
        # Executors will be initialized here or on demand
        self.spotify_executor = SpotifyExecutor()
        self.youtube_executor = YouTubeExecutor()
        self.local_executor = LocalExecutor()

    def plan(self, intent: Intent) -> ExecutionPlan:
        """
        Layer 2: Platform Resolution Logic.
        Decides WHERE to play the media.
        """
        action = intent.action.lower()
        
        if action not in ["play", "resume", "pause", "next", "previous"]:
             # Fallback for unknown media actions
             print(f"[MediaPlanner] Unsupported action: {action}")
             return ExecutionPlan(intent=intent, steps=[])

        if action == "play":
            query = intent.parameters.get("query", "")
            platform_hint = intent.parameters.get("platform_hint")
            
            # 1. Resolve Platform
            target_platform = self._resolve_platform(query, platform_hint)
            print(f"[MediaPlanner] Resolved Platform: {target_platform.value}")

            # 2. delegate to specific executor to get the plan steps
            steps, verification = self._get_executor_plan(target_platform, intent)
            
            # 3. Add fallback logic metadata?
            # ideally the AutomationEngine should handle fallback if a step fails, 
            # OR we return a plan that includes conditional jumps (too complex for now).
            # For this strictly sequential engine, we will rely on the Automation Engine
            # or a higher level "Controller" to handle fallback. 
            # BUT, the prompt asks for "Fail in one layer NEVER corrupts another".
            # "Retry same platform see once -> Then fallback".
            
            # Since our ExecutionPlan is linear, we might need a "Smart" Step
            # or we return a High Level "PlayMedia" step that the AutomationEngine
            # knows how to retry/fallback.
            # HOWEVER, the prompt implies "Platform-Specific Execution Plans".
            
            # We will return the plan for the *primary* resolved platform.
            # If that fails, the System (Main Loop) should catch the failure, 
            # consult the Learning Layer / Planner again, and request a fallback.
            
            return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)

        return ExecutionPlan(intent=intent, steps=[])

    def _resolve_platform(self, query: str, hint: Optional[str]) -> MediaPlatform:
        # 1. Explicit Constraint
        if hint:
            try:
                return MediaPlatform(hint.lower())
            except ValueError:
                print(f"[MediaPlanner] Invalid platform hint '{hint}', falling back to auto.")
        
        # 2. Last Successful Platform / User Preference
        learned_platform = self.learning_layer.get_preferred_platform(song_name=query)
        if learned_platform:
            try:
                return MediaPlatform(learned_platform.lower())
            except ValueError:
                pass
        
        # 3. Default Priority
        return MediaPlatform.SPOTIFY

    def _get_executor_plan(self, platform: MediaPlatform, intent: Intent):
        if platform == MediaPlatform.SPOTIFY:
            return self.spotify_executor.create_play_plan(intent)
        elif platform == MediaPlatform.YOUTUBE:
            return self.youtube_executor.create_play_plan(intent)
        elif platform == MediaPlatform.LOCAL:
            return self.local_executor.create_play_plan(intent)
        else:
             return [], None
