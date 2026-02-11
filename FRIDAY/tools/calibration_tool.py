import json
import os
import time
import pyautogui

CONFIG_PATH = os.path.join(os.getcwd(), "FRIDAY", "config", "media_ui_map.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"spotify": {}, "youtube": {}}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"spotify": {}, "youtube": {}}

def save_config(data):
    # Ensure dir exists
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Configuration saved to {CONFIG_PATH}")

def calibrate():
    print("=== Media Control Calibration Mode ===")
    print("We will calibrate mouse positions for Spotify and YouTube.")
    print("Please open Spotify and your Browser to YouTube now.")
    print("Maximize both windows if possible.")
    input("Press Enter when ready...")

    data = load_config()

    # Spotify
    print("\n--- Calibrating Spotify ---")
    print("Switch to Spotify Window.")
    input("Press Enter when Spotify is active...")
    
    print("Hover your mouse over the SEARCH BAR/BUTTON.")
    time.sleep(1)
    for i in range(3, 0, -1):
        print(f"Capturing in {i}...")
        time.sleep(1)
    
    x, y = pyautogui.position()
    print(f"Captured: ({x}, {y})")
    data["spotify"]["search_bar"] = {"x": x, "y": y}
    
    print("Now perform a search (any song) and wait for results.")
    print("Hover your mouse over the FIRST TRACK result (the play area/text).")
    input("Press Enter when ready to capture First Result...")
    
    for i in range(3, 0, -1):
        print(f"Capturing in {i}...")
        time.sleep(1)
        
    x, y = pyautogui.position()
    print(f"Captured: ({x}, {y})")
    data["spotify"]["first_result"] = {"x": x, "y": y}
    data["spotify"]["calibrated"] = True

    # YouTube
    print("\n--- Calibrating YouTube ---")
    print("Switch to your Browser with YouTube open.")
    input("Press Enter when YouTube is active...")
    
    print("Hover your mouse over the SEARCH BAR.")
    time.sleep(1)
    for i in range(3, 0, -1):
        print(f"Capturing in {i}...")
        time.sleep(1)
    
    x, y = pyautogui.position()
    print(f"Captured: ({x}, {y})")
    data["youtube"]["search_bar"] = {"x": x, "y": y}

    print("Now perform a search and wait for results.")
    print("Hover your mouse over the FIRST VIDEO title/thumbnail.")
    input("Press Enter when ready to capture First Video...")

    for i in range(3, 0, -1):
        print(f"Capturing in {i}...")
        time.sleep(1)

    x, y = pyautogui.position()
    print(f"Captured: ({x}, {y})")
    data["youtube"]["first_video"] = {"x": x, "y": y}
    data["youtube"]["calibrated"] = True

    save_config(data)
    print("\nCalibration Complete! GMC is now ready.")

def verify_calibration():
    print("=== Configuration Verification ===")
    data = load_config()
    
    for platform in ["spotify", "youtube"]:
        print(f"\nChecking {platform.upper()}...")
        coords = data.get(platform, {})
        if not coords.get("calibrated"):
            print("Not calibrated.")
            continue
            
        for key, val in coords.items():
            if key == "calibrated": continue
            print(f"Moving to {key}: ({val['x']}, {val['y']})")
            pyautogui.moveTo(val['x'], val['y'], duration=1.0)
            time.sleep(0.5)
    
    print("\nVerification movement done.")

if __name__ == "__main__":
    print("1. Calibrate")
    print("2. Verify Calibration (Move Mouse)")
    choice = input("Select (1/2): ")
    if choice == "2":
        verify_calibration()
    else:
        calibrate()
