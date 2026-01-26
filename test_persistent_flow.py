
import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())

# We import Automation normally, then patch internals
from Backend import Automation

@patch('Backend.Automation.win32gui')
@patch('Backend.Automation.pyautogui')
@patch('Backend.Automation.webbrowser')
def test_persistent_flow(mock_web, mock_gui, mock_win32):
    print("\n--- TEST: Persistent WhatsApp Flow (Verified Logic) ---")
    
    # 1. Setup mocks
    mock_win32.IsWindowVisible.return_value = True
    mock_win32.GetWindowText.return_value = "WhatsApp"
    mock_win32.GetWindowRect.return_value = (0, 0, 1000, 800)
    mock_win32.GetForegroundWindow.return_value = 12345
    
    # EnumWindows mock
    def side_effect_enum(callback, handles):
        callback(12345, handles)
    mock_win32.EnumWindows.side_effect = side_effect_enum
    
    # Text side effect for header check
    mock_win32.GetWindowText.side_effect = ["WhatsApp", "WhatsApp", "WhatsApp - Brother", "WhatsApp - Brother", "WhatsApp - Brother", "WhatsApp - Brother"]

    # 2. Run
    print("Executing secure_send_whatsapp...")
    # Adjust time.sleep to run faster during test? 
    # We can patch time.sleep but wait_until uses time.time()
    
    res = Automation.secure_send_whatsapp("Brother", "Msg")
    print(f"Result: {res}")
    
    if res:
        print("[PASS] Flow succeeded")
    else:
        print("[FAIL] Flow failed")

if __name__ == "__main__":
    test_persistent_flow()
