import json
import os
from typing import List, Tuple
from FRIDAY.core.models import Intent, AutomationAction, VerificationResult, AutomationAction as Action
from FRIDAY.layers.executors.base_executor import BaseExecutor

class SpotifyExecutor(BaseExecutor):
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
        spotify_cfg = self.config.get("spotify", {})
        
        # Calibration check
        if not spotify_cfg.get("calibrated"):
             # In robust mode, we should perhaps warn?
             # But we proceed with fallback or just calibrated logic assuming it exists.
             pass

        search_bar_coords = spotify_cfg.get("search_bar")
        first_result_coords = spotify_cfg.get("first_result")

        # STEP 1: OPEN & STABILIZE
        steps.append(Action(type="open_app", params={"app_name": "Spotify"}))
        steps.append(Action(type="wait_for_window", params={"title": "Spotify", "timeout": 10.0}))
        
        # Add explicit wait for app internal loading (even if window is visible)
        steps.append(Action(type="wait", params={"seconds": 3.0}))
        
        # Maximize for consistency
        steps.append(Action(type="press_key", params={"key": "win+up"}))
        steps.append(Action(type="wait", params={"seconds": 1.0})) # Short wait for anim

        # STEP 2: HARD RESET PLAYER
        # Stop media to ensure we detect new playback
        steps.append(Action(type="press_key", params={"key": "stop"})) 
        steps.append(Action(type="wait", params={"seconds": 0.5})) # Wait for stop to register

        # STEP 3: SEARCH INPUT CONFIRMATION
        # Focus Search
        if search_bar_coords:
             # Click search bar to be sure? Use Ctrl+L as primary.
             steps.append(Action(type="click_at", params={"x": search_bar_coords["x"], "y": search_bar_coords["y"]}))
        else:
             steps.append(Action(type="press_key", params={"key": "ctrl+l"}))
        
        # Capture Hash of Search Bar (Context: 'search_bar_empty') 
        # Actually, we want to capture, type, then wait for change.
        # But we don't know the region of search bar dynamically unless we assume around calibration point.
        # Let's use a small region around calibrated point? 
        # If no region, we wait for *full screen* change? That works too (text typing changes screen).
        
        steps.append(Action(type="capture_ui_hash", params={"save_key": "pre_type_hash"}))
        
        # Clear & Type
        steps.append(Action(type="press_key", params={"key": "ctrl+a"}))
        steps.append(Action(type="press_key", params={"key": "backspace"}))
        
        search_query = f"track:{query}"
        steps.append(Action(type="type_text", params={"text": search_query}))
        
        # Wait for Search Bar/UI to change (Typing reflected)
        steps.append(Action(type="wait_for_ui_change", params={"initial_hash_key": "pre_type_hash", "timeout": 10.0}))
        
        # Wait for Results to Load / UI to Stabilize
        # Results take time. We wait for UI to be stable for 0.5s
        # Increased timeout to 15s to handle slow network/loading animations
        # User Feedback: "Add result-stabilization wait loop before Spotify click"
        # We use strict wait_for_ui_stable here.
        steps.append(Action(type="wait_for_ui_stable", params={"duration": 1.5, "timeout": 15.0}))

        # STEP 4: TRACK SELECTION
        if first_result_coords:
            # Capture hash before click (to verify click did something?)
            steps.append(Action(type="capture_ui_hash", params={"save_key": "pre_click_hash"}))
            
            # Double click calibrated
            steps.append(Action(type="double_click_at", params={"x": first_result_coords["x"], "y": first_result_coords["y"]}))
            
            # Verify UI Changed (Playback started, bottom bar changed, or highlight changed)
            steps.append(Action(type="wait_for_ui_change", params={"initial_hash_key": "pre_click_hash", "timeout": 10.0}))
        else:
             # Fallback
             steps.append(Action(type="press_key", params={"key": "tab"}))
             steps.append(Action(type="press_key", params={"key": "enter"}))

        # STEP 5: VERIFICATION
        # Hybrid Verification
        # 1. Active Window
        verification = Action(type="verify_active_window", params={"app_name": "Spotify"})
        # 2. Audio Activity (Chain verification?)
        # Currently models.AutomationAction verification is single check.
        # But we can verify multiple things in 'steps' (as assertions) or combine them.
        # verification_engine mostly takes one action.
        # But we can update the plan to include manual verification steps?
        # NO, verification_step in plan is the FINAL check.
        # Let's execute verification as a final STEP in the plan if we want multiple?
        # Or standard verification returns success.
        
        # NOTE: User wants "Audio verification...".
        # We can implement a "verify_media_playing" that checks both?
        # For now, let's stick to active window or try audio if possible.
        # Let's change verification to "verify_audio_activity" since that's stronger proof of playback.
        verification = Action(type="verify_audio_activity", params={"app_name": "Spotify"})
        
        return steps, verification
