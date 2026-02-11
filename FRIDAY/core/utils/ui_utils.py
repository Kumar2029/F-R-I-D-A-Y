import time
import pyautogui
import hashlib
from typing import Optional, Tuple
try:
    import win32gui
except ImportError:
    win32gui = None

def get_foreground_window_title() -> str:
    if not win32gui: return ""
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    except:
        return ""

def wait_for_window(title_substring: str, timeout: float = 10.0) -> bool:
    """
    Waits for a window containing title_substring to be in the foreground.
    """
    start_time = time.time()
    print(f"[UI] Waiting for window '{title_substring}'...")
    while time.time() - start_time < timeout:
        current_title = get_foreground_window_title()
        if title_substring.lower() in current_title.lower():
            return True
        time.sleep(0.5)
    print(f"[UI] Timeout waiting for window '{title_substring}'")
    return False

def get_ui_hash(region: Optional[Tuple[int, int, int, int]] = None) -> str:
    """
    Captures a screenshot of the region (x, y, w, h) and returns its MD5 hash.
    If region is None, captures full screen.
    """
    try:
        img = pyautogui.screenshot(region=region)
        # Convert to bytes
        img_bytes = img.tobytes()
        return hashlib.md5(img_bytes).hexdigest()
    except Exception as e:
        print(f"[UI] Hash Error: {e}")
        return "error_hash"

def wait_for_ui_change(region: Optional[Tuple[int, int, int, int]], initial_hash: str, timeout: float = 10.0) -> bool:
    """
    Waits for the UI hash to be DIFFERENT from initial_hash.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_hash = get_ui_hash(region)
        if current_hash != initial_hash:
            return True
        time.sleep(0.2)
    return False

def wait_for_ui_stable(region: Optional[Tuple[int, int, int, int]], duration: float = 1.0, timeout: float = 10.0) -> bool:
    """
    Waits for the UI hash to remain CONSTANT for `duration` seconds.
    """
    start_time = time.time()
    stable_start = time.time()
    last_hash = get_ui_hash(region)
    
    while time.time() - start_time < timeout:
        current_hash = get_ui_hash(region)
        if current_hash == last_hash:
            if time.time() - stable_start >= duration:
                return True
        else:
            last_hash = current_hash
            stable_start = time.time() # Reset stability timer
            
        time.sleep(0.1)
    
    return False
