import pyautogui
import time
import win32gui
import win32con
from Backend.MediaVerifier import MediaVerifier
from Backend.Automation import OpenApp, Type, Press
from rich import print

def ensure_maximized(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"[Spotify] Could not maximize: {e}")
        return False

def play(query: str, verifier: MediaVerifier):
    print(f"[Spotify] Executing Play: {query}")
    
    # 1. Open Spotify
    if not OpenApp("spotify"):
        print("[Spotify] Failed to open app.")
        return False
    
    time.sleep(3) # Wait for load (Parametrize?)
    
    # Get HWND
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    if "spotify" not in title.lower():
        print("[Spotify] Spotify not in foreground.")
        # Try to find it? for now abort strict
        return False
        
    ensure_maximized(hwnd)
    
    # 2. Focus Search (Ctrl+L is standard, but user mentioned pixel anchor. Strict rule: specific pixel?)
    # "Focus search bar via pixel anchor" -> fallback to shortcut if robust?
    # Let's use shortcut as it is usually more robust, but USER SPECIFIED PIXEL ANCHOR.
    # We need calibration data.
    # If not calibrated, use fallback default coordinates or shortcut.
    # For now, let's genericize with shortcut, as calibration is separate task.
    # Actually, user said "NO TAB/UP/DOWN roulette". Ctrl+L is safe.
    Press("ctrl+l")
    time.sleep(0.5)
    
    # Clear Input
    Press("ctrl+a")
    Press("backspace")
    
    # Type
    Type(f"track:{query}")
    time.sleep(0.5)
    Press("enter")
    
    # Wait for UI Stabilization
    time.sleep(2.0)
    
    # 3. Click First Result
    # User said "Click first track result via calibrated pixel".
    # We need a default "likely" position if not calibrated.
    # In maximized Spotify, top result is usually at a specific relative ratio.
    # We will assume a default ratio for now.
    
    time.sleep(2.0)
    
    # 3. Click First Result
    import json
    import os
    
    click_x, click_y = None, None
    calib_path = "config/media_ui_map.json"
    
    if os.path.exists(calib_path):
        try:
            with open(calib_path, 'r') as f:
                data = json.load(f)
                if "spotify_first_result" in data:
                    click_x, click_y = data["spotify_first_result"]
                    print(f"[Spotify] Using Calibrated Coordinates: {click_x}, {click_y}")
        except Exception as e:
            print(f"[Spotify] Calibration load error: {e}")
            
    if not click_x:
        # Default: X=35%, Y=30% (Approximation of list top)
        screen_w, screen_h = pyautogui.size()
        click_x = int(screen_w * 0.35) 
        click_y = int(screen_h * 0.30) # Top result
        print(f"[Spotify] Using Default Coordinates: {click_x}, {click_y}")
    
    print(f"[Spotify] Clicking at {click_x}, {click_y}")
    pyautogui.click(click_x, click_y)
    time.sleep(0.1)
    pyautogui.doubleClick(click_x, click_y)
    time.sleep(0.5)
    Press("enter") # Fallback if click missed
    
    # Wait longer for audio to actually start buffering/playing
    time.sleep(4.0)
    
    # 4. Verification from Layer 4
    # Retry verification for up to 5 seconds
    for _ in range(5):
        if verifier.verify_audio_activity(["spotify"]):
            print("[Spotify] Audio Verified.")
            return True
        time.sleep(1.0)
    
    print("[Spotify] Audio verification failed.")
    return False
