import time
import pyautogui
import win32gui
import os
from FRIDAY.core.models import AutomationAction, VerificationResult

class VerificationEngine:
    def verify(self, action: AutomationAction) -> VerificationResult:
        if not action:
            return VerificationResult(True, message="No verification required")

        print(f"[Verification] Verifying: {action.type} - {action.params}")
        
        try:
            match action.type:
                case "verify_media_title":
                    return self._verify_window_title(
                        action.params.get("expected_title"), 
                        action.params.get("app_name")
                    )
                
                case "verify_browser_title":
                    return self._verify_window_title(
                        action.params.get("expected_substring")
                    )

                case "verify_file_exists":
                    path = action.params.get("path")
                    if os.path.exists(path):
                        return VerificationResult(True, message=f"File found: {path}")
                    return VerificationResult(False, error_message=f"File not found: {path}")

                case _:
                    print(f"[Verification] Unknown type: {action.type}")
                    return VerificationResult(False, error_message=f"Unknown verification type {action.type}")

        except Exception as e:
            return VerificationResult(False, error_message=str(e))

    def _verify_window_title(self, expected_substring: str, app_name: str = None) -> VerificationResult:
        matches = []
        def callback(hwnd, matches):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                if not title: return
                if expected_substring.lower() in title:
                    matches.append(title)
        
        try:
            win32gui.EnumWindows(callback, matches)
            if matches:
                return VerificationResult(True, message=f"Found matching window: {matches[0]}")
            return VerificationResult(False, error_message=f"No window found containing '{expected_substring}'")
        except Exception as e:
             return VerificationResult(False, error_message=f"Window enum error: {e}")
