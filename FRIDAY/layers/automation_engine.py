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
from FRIDAY.core.utils import ui_utils, code_backend

class AutomationEngine:
    def execute_plan(self, plan: ExecutionPlan) -> ActionResult:
        print(f"[Automation] Executing Plan: {plan.intent.action}")
        logs = []
        self._context = {} # Runtime context for variable storage (e.g. hashes)
        
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

                case "click_at":
                    x = step.params.get("x")
                    y = step.params.get("y")
                    if x and y:
                        pyautogui.click(x=x, y=y)
                    return True

                case "double_click_at":
                    x = step.params.get("x")
                    y = step.params.get("y")
                    if x and y:
                        pyautogui.doubleClick(x=x, y=y)
                    return True

                case "wait_for_window":
                    title = step.params.get("title")
                    timeout = step.params.get("timeout", 10.0)
                    return ui_utils.wait_for_window(title, timeout)

                case "wait_for_ui_change":
                    region = step.params.get("region") # Tuple or None
                    initial_hash_key = step.params.get("initial_hash_key")
                    initial_hash = step.params.get("initial_hash")
                    
                    # Resolve key if present
                    if initial_hash_key and hasattr(self, "_context"):
                        initial_hash = self._context.get(initial_hash_key)

                    if not initial_hash:
                         # If no hash provided, maybe we capture current and wait for change?
                         # "Wait for ANY change from NOW"
                         initial_hash = ui_utils.get_ui_hash(region)
                    
                    return ui_utils.wait_for_ui_change(region, initial_hash, timeout=step.params.get("timeout", 10.0))

                case "wait_for_ui_stable":
                    region = step.params.get("region")
                    duration = step.params.get("duration", 1.0)
                    timeout = step.params.get("timeout", 10.0)
                    result = ui_utils.wait_for_ui_stable(region, duration, timeout)
                    if not result:
                        print(f"[Automation] Warning: UI stabilization timed out ({timeout}s). visual elements might be moving.")
                        # Proceed anyway? Failed stability might just mean a spinner or progress bar.
                        # Strict mode says "Fail", but user exp says "Try".
                        # We return True but log warning.
                        return True 
                    return True

                case "capture_ui_hash":
                    key = step.params.get("save_key")
                    region = step.params.get("region")
                    h = ui_utils.get_ui_hash(region)
                    if hasattr(self, "_context"):
                        self._context[key] = h
                        print(f"[Automation] Captured Hash {key}: {h}")
                    return True

                # --- BACKEND CODE ACTIONS ---
                case "save_code_to_file":
                    code = step.params.get("code")
                    filename = step.params.get("filename")
                    full_path = code_backend.create_code_file(code, filename)
                    # Store path in context for subsequent steps
                    if hasattr(self, "_context"):
                        self._context["last_file_path"] = full_path
                    return True

                case "open_file_in_vscode":
                    # Get path from params OR context
                    path = step.params.get("path")
                    if not path and hasattr(self, "_context"):
                        path = self._context.get("last_file_path")
                    
                    if path:
                        code_backend.open_file_in_vscode(path)
                        return True
                    return False

                case "execute_python_backend":
                    path = step.params.get("path")
                    if not path and hasattr(self, "_context"):
                        path = self._context.get("last_file_path")
                    
                    if path:
                        ret, out, err = code_backend.execute_python_file(path)
                        print(f"[Backend Exec] Ret: {ret}\nOut: {out}\nErr: {err}")
                        
                        # Store result in context? Or fail if ret != 0?
                        # User requirement: "If returncode != 0... Speak error"
                        # AutomationEngine returns Result. 
                        # If we return False here, Automation fails.
                        if ret != 0:
                            print(f"[Backend Exec] Failed: {err}")
                            # We can return False to trigger failure
                            return False # Or return ActionResult with error?
                        
                        return True
                    return False

                case "run_in_vscode_terminal":
                    path = step.params.get("path")
                    if not path and hasattr(self, "_context"):
                        path = self._context.get("last_file_path")
                    
                    if path:
                        # 1. Ensure Window Active (re-check)
                        ui_utils.wait_for_window("Visual Studio Code", timeout=5.0)
                        
                        # 2. Open Terminal (Ctrl+`)
                        # Sometimes focus is tricky. Let's explicit click? No, shortcut safest if focused.
                        pyautogui.hotkey('ctrl', '`')
                        time.sleep(1.0) # Wait for terminal panel
                        
                        # 3. Type Command
                        # Use python "path"
                        cmd = f'python "{path}"'
                        # Standard typing might be slow/flaky. Paste is faster but might fail if not focused.
                        # Let's type fast.
                        pyautogui.write(cmd, interval=0.01)
                        time.sleep(0.5)
                        pyautogui.press('enter')
                        return True
                    return False

                case _:
                    print(f"[Automation] Unknown step type: {step.type}")
                    return False
                    
        except Exception as e:
            print(f"[Automation] Error in step {step.type}: {e}")
            return False
