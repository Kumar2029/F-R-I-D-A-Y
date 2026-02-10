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

                case "verify_active_window":
                    return self._verify_active_window(
                         action.params.get("app_name")
                    )

                case "verify_file_exists":
                    path = action.params.get("path")
                    if os.path.exists(path):
                        return VerificationResult(True, message=f"File found: {path}")
                    return VerificationResult(False, error_message=f"File not found: {path}")

                case "verify_command_execution":
                    return self._verify_command_execution(
                         action.params.get("command")
                    )

                case "verify_success_signal":
                    return VerificationResult(True, message="GMC Execution Successful")

                case "verify_fail_signal":
                    return VerificationResult(False, error_message=action.params.get("reason", "Unknown Failure"))

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

    def _verify_active_window(self, app_name: str) -> VerificationResult:
        try:
             hwnd = win32gui.GetForegroundWindow()
             title = win32gui.GetWindowText(hwnd).lower()
             print(f"[Verification] Active Window: {title}")
             
             if not app_name:
                 return VerificationResult(False, error_message="No app name provided for verification")
                 
             if app_name.lower() in title:
                 return VerificationResult(True, message=f"App '{app_name}' is in foreground.")
            
             # Special casing for Spotify where title changes to "Artist - Song"
             if app_name.lower() == "spotify" and " - " in title:
                 return VerificationResult(True, message=f"Spotify Likely Active (Playing: {title})")

             # Fallback: Check if app_name is in the process name? (Harder with just win32gui)
             # Strict verification requires title match for now.
             return VerificationResult(False, error_message=f"Active window '{title}' does not contain '{app_name}'")
        except Exception as e:
             return VerificationResult(False, error_message=f"Active window check failed: {e}")

    def _verify_command_execution(self, command: str) -> VerificationResult:
        try:
            print(f"[Verification] Running command: {command}")
            import subprocess
            # Capture output
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return VerificationResult(True, message=f"Command executed successfully. Output: {output[:100]}...")
            else:
                error = result.stderr.strip()
                return VerificationResult(False, error_message=f"Command failed (Exit {result.returncode}): {error}")
        except Exception as e:
            return VerificationResult(False, error_message=f"Command verification failed: {e}")
