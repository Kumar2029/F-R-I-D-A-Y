import webbrowser
import time
from Backend.MediaVerifier import MediaVerifier
from rich import print
import pyautogui

def play(query: str, verifier: MediaVerifier):
    print(f"[YouTube] Executing Play: {query}")
    
    # 1. Construct URL
    # Auto-play first result: "https://www.youtube.com/results?search_query=..." requires clicking.
    # Better: "https://www.youtube.com/watch?v=..." (Need to fetch?)
    # User flow: "Open results -> Click first video"
    
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)
    
    time.sleep(5.0) # Wait for page load
    
    # 2. Click First Video via Pixel Anchor
    import json
    import os
    
    click_x, click_y = None, None
    calib_path = "config/media_ui_map.json"
    
    if os.path.exists(calib_path):
        try:
            with open(calib_path, 'r') as f:
                data = json.load(f)
                if "youtube_first_result" in data:
                    click_x, click_y = data["youtube_first_result"]
                    print(f"[YouTube] Using Calibrated Coordinates: {click_x}, {click_y}")
        except Exception as e:
            print(f"[YouTube] Calibration load error: {e}")

    if not click_x:
        # Default: X=35%, Y=25% (Similar to Spotify list)
        screen_w, screen_h = pyautogui.size()
        click_x = int(screen_w * 0.35)
        click_y = int(screen_h * 0.25)
        print(f"[YouTube] Using Default Coordinates: {click_x}, {click_y}")
    
    pyautogui.click(click_x, click_y)
    
    time.sleep(5.0) # Wait for ad / load
    
    # 3. Verify
    # Check window title contains "YouTube"?
    # Check audio?
    if verifier.verify_audio_activity(["chrome", "firefox", "edge", "opera"]):
        return True
        
    return False
