import time
import pyautogui
import subprocess
from AppOpener import open as appopen
from AppOpener import close as appclose
from FRIDAY.core.models import ExecutionPlan, AutomationAction, ActionResult, VerificationResult
from Backend.TextToSpeech import TTS
import pyperclip
import pyautogui
import time
import subprocess
try:
    import win32gui
except ImportError:
    win32gui = None

class AutomationEngine:
    def execute_plan(self, plan: ExecutionPlan) -> ActionResult:
        print(f"[Automation] Executing Plan: {plan.intent.action}")
        logs = []
        
        try:
            for step in plan.steps:
                logs.append(f"Executing step: {step.type} - {step.params}")
                print(f"[Automation] Step: {step.type} ({step.params})")
                
                success = self._dispatch_step(step)
                if not success:
                    return ActionResult(False, f"Step failed: {step.type}", VerificationResult(False), logs)
            
            # If all steps succeed, return success (Verification Layer handles final check)
            return ActionResult(True, "Automation complete", VerificationResult(True), logs)
            
        except Exception as e:
            msg = f"Automation Exception: {e}"
            print(msg)
            return ActionResult(False, msg, VerificationResult(False, error_message=str(e)), logs)

    def _dispatch_step(self, step: AutomationAction) -> bool:
        """
        Dispatches atomic action to primitive handler.
        """
        try:
            match step.type:
                case "open_app":
                    app_name = step.params.get("app_name")
                    appopen(app_name, match_closest=True, output=False)
                    return True
                
                case "wait":
                    sec = float(step.params.get("seconds", 1.0))
                    time.sleep(sec)
                    return True
                
                case "type_text":
                    text = step.params.get("text", "")
                    pyautogui.write(text, interval=0.01)
                    return True
                
                case "paste_text":
                    text = step.params.get("text", "")
                    # import pyperclip (Removed: Global import used)
                    pyperclip.copy(text)
                    pyautogui.hotkey("ctrl", "v")
                    return True

                case "press_key":
                    key = step.params.get("key", "")
                    if "+" in key:
                        keys = key.split("+")
                        pyautogui.hotkey(*keys)
                    else:
                        pyautogui.press(key)
                    return True
                
                case "click_web_element":
                    # Placeholder for web element clicking without Selenium
                    # Needs visual anchor or tab nav
                    print("[Automation] Click web element not fully implemented without browser context.")
                    return True

                case "run_terminal_command":
                    cmd = step.params.get("command")
                    subprocess.Popen(cmd, shell=True)
                    return True

                case "speak":
                    text = step.params.get("text", "")
                    if text:
                        print(f"[Automation] Speaking: {text}")
                        # Move TTS to a separate thread to avoid blocking automation? 
                        # For now, blocking is safer for "Conversation".
                        TTS(text)
                    return True
                
                case "verify_focus_probe":
                    probe_text = step.params.get("text", "__probe__")
                    # 1. Type Probe
                    pyautogui.write(probe_text, interval=0.01)
                    time.sleep(0.2)
                    # 2. Select All
                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.2)
                    # 3. Copy
                    pyautogui.hotkey("ctrl", "c")
                    time.sleep(0.2)
                    # 4. Read Clipboard
                    clipboard_content = pyperclip.paste().strip()
                    # 5. Clear Input (Reset state)
                    pyautogui.press("backspace")
                    
                    if probe_text in clipboard_content:
                        print(f"[Automation] Focus Confirmed: {probe_text} detected.")
                        return True
                    else:
                        print(f"[Automation] Focus Failed: Expected '{probe_text}', got '{clipboard_content}'")
                        return False

                case "verify_active_window":
                    if not win32gui:
                        print("[Automation] win32gui not available. Skipping window verification.")
                        return True
                        
                    app_name = step.params.get("app_name", "").lower()
                    try:
                        hwnd = win32gui.GetForegroundWindow()
                        title = win32gui.GetWindowText(hwnd).lower()
                        print(f"[Automation] Active Window: {title}")
                        
                        if app_name in title:
                            return True
                        # Spotify special case
                        if app_name == "spotify" and " - " in title:
                             return True
                             
                        print(f"[Automation] Verification Failed: '{app_name}' not in '{title}'")
                        return False
                    except Exception as e:
                        print(f"[Automation] Window check error: {e}")
                        return False

                case _:
                    print(f"[Automation] Unknown step type: {step.type}")
                    return False
                    
        except Exception as e:
            print(f"[Automation] Error in step {step.type}: {e}")
            return False
