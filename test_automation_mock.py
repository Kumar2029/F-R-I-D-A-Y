
import sys
import os
import time
sys.path.append(os.getcwd())

# Mock libraries BEFORE importing Automation
from unittest.mock import MagicMock, patch

# Mock modules that interact with the OS
sys.modules['pyautogui'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['AppOpener'] = MagicMock()
sys.modules['pywhatkit'] = MagicMock()
sys.modules['win32gui'] = MagicMock()
sys.modules['keyboard'] = MagicMock()

# Import Automation after mocking
from Backend.Automation import OpenApp, Type, Press, System, FocusWindow
import Backend.Automation as AuthModule # To access internal mocks if needed

# Setup Mock behavior
def test_whatsapp_workflow():
    print("\n--- TEST: WhatsApp Open & Focus Logic ---")
    
    # Mock FocusWindow to fail first 3 times then succeed (simulating load delay)
    focus_calls = {"count": 0}
    def side_effect_focus(app_name):
        focus_calls["count"] += 1
        print(f"FocusWindow called for '{app_name}' (Attempt {focus_calls['count']})")
        return focus_calls["count"] > 3 # Succeed on 4th try
    
    # We need to patch the FocusWindow used INSIDE Automation.OpenApp
    # Since we imported OpenApp, it uses the global FocusWindow in that module.
    # We can patch `Backend.Automation.FocusWindow`.
    
    with patch('Backend.Automation.FocusWindow', side_effect=side_effect_focus) as mock_focus:
        # Run OpenApp("whatsapp")
        # It should call webbrowser.open, then poll FocusWindow
        
        start_time = time.time()
        success = OpenApp("whatsapp")
        end_time = time.time()
        
        print(f"OpenApp returned: {success}")
        print(f"Time taken: {end_time - start_time:.2f}s (Expected > 3s due to attempts)")
        
        if success and focus_calls["count"] >= 4:
            print("[PASS] WhatsApp workflow polled and succeeded.")
        else:
            print(f"[FAIL] Workflow failed. Focus calls: {focus_calls['count']}")

def test_system_commands():
    print("\n--- TEST: System Commands (Volume/Mute) ---")
    
    cmds = ["mute", "volume up", "volume down"]
    for cmd in cmds:
        success = System(cmd)
        if success:
            print(f"[PASS] System command '{cmd}' executed.")
        else:
            print(f"[FAIL] System command '{cmd}' failed.")

def test_type_delay():
    print("\n--- TEST: Type Command Delay ---")
    # Verify Type waits for focus
    start = time.time()
    Type("Hello World")
    dur = time.time() - start
    print(f"Type duration: {dur:.2f}s (Expected ~3s default delay)")
    
    if dur >= 3.0:
        print("[PASS] Type command respects safety delays.")
    else:
        print("[FAIL] Type command too fast!")

if __name__ == "__main__":
    test_whatsapp_workflow()
    test_type_delay()
    test_system_commands()
