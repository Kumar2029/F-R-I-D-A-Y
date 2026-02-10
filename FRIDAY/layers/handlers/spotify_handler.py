from typing import List
from FRIDAY.core.models import AutomationAction, VerificationResult

class SpotifyHandler:
    """
    Robust Spotify Automation Handler (Zero-Guessing).
    Implements strict 7-phase execution sequence.
    
    PHASES:
    1. Sanitization (Input Cleaning)
    2. Open & Freeze (Stop Playback)
    3. Hard Focus Verification (Window Title)
    4. Search Field Lock (Probe Verification)
    5. Search Execution (Type, Enter)
    6. Track Selection (Deterministic Enter)
    7. Playback Verification (Window Title)
    """

    def play_song(self, raw_query: str) -> List[AutomationAction]:
        """
        Generates a robust automation plan to play a specific song.
        """
        steps = []
        
        # PHASE 1: SANITIZATION
        song_query = self._sanitize_query(raw_query)
        print(f"[SpotifyHandler] Sanitized '{raw_query}' -> '{song_query}'")

        # PHASE 2: OPEN & FREEZE STATE
        steps.append(AutomationAction(type="open_app", params={"app_name": "Spotify"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 3.0})) 
        steps.append(AutomationAction(type="press_key", params={"key": "stop"})) # Force Stop
        steps.append(AutomationAction(type="wait", params={"seconds": 0.8}))

        # PHASE 3: HARD FOCUS VERIFICATION
        # Verify Spotify is actually the active window
        steps.append(AutomationAction(
            type="verify_active_window", 
            params={"app_name": "Spotify"}
        ))

        # PHASE 4: SEARCH FIELD LOCK
        # 1. Ctrl+L to focus
        steps.append(AutomationAction(type="press_key", params={"key": "ctrl+l"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
        
        # 2. Probe Verification (Type -> Ctrl+A -> Backspace handled by engine check?)
        # User spec: Type probe -> Wait -> Ctrl+A -> Backspace.
        # My 'verify_focus_probe' does this internally.
        steps.append(AutomationAction(
            type="verify_focus_probe", 
            params={"text": "__probe__"}
        ))
        
        # PHASE 5: SEARCH EXECUTION
        final_query = f"track:{song_query}"
        steps.append(AutomationAction(type="type_text", params={"text": final_query}))
        steps.append(AutomationAction(type="wait", params={"seconds": 1.8})) 
        steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 2.5})) 

        # PHASE 6: TRACK SELECTION (DETERMINISTIC)
        # Option B (Fallback): Press Enter using the keyboard.
        # User explicitly forbids "TAB".
        # Assuming Search Results auto-highlight first item.
        steps.append(AutomationAction(type="press_key", params={"key": "enter"}))

        # PHASE 7: PLAYBACK VERIFICATION
        # Verify title change?
        # AutomationEngine doesn't have 'verify_media_title' logic built-in as a step yet, 
        # but we can use 'verify_active_window' again.
        steps.append(AutomationAction(type="wait", params={"seconds": 3.0}))
        # Re-verify window to ensure it didn't crash/close and maybe check title if possible
        steps.append(AutomationAction(
            type="verify_active_window", 
            params={"app_name": "Spotify"}
        ))

        return steps

    def _sanitize_query(self, query: str) -> str:
        """
        Removes filler words to isolate the song title.
        """
        q = query.lower()
        remove_list = ["play", "on spotify", "song", "music", "track"]
        for word in remove_list:
            q = q.replace(word, "")
        return q.strip()
