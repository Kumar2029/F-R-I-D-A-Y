
import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())

# Mock Windows API logic BEFORE importing Automation
sys.modules['win32gui'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['AppOpener'] = MagicMock()
sys.modules['pywhatkit'] = MagicMock()

# Import modules to test
from Backend.Automation import secure_whatsapp_workflow, WHATSAPP_SEARCH_RATIO_X
from Backend.OutcomeVerifier import OutcomeVerifier

def test_secure_workflow_success():
    print("\n--- TEST: Secure WhatsApp Workflow (Success Path) ---")
    
    # Mock win32gui to find window and report it as foreground
    mock_hwnd = 12345
    
    # EnumWindows mock setup
    def side_effect_enum(callback, handles):
        # Simulate finding the window
        callback(mock_hwnd, handles)
        
    sys.modules['win32gui'].EnumWindows.side_effect = side_effect_enum
    sys.modules['win32gui'].IsWindowVisible.return_value = True
    sys.modules['win32gui'].GetWindowText.return_value = "WhatsApp"
    sys.modules['win32gui'].GetForegroundWindow.return_value = mock_hwnd
    sys.modules['win32gui'].GetWindowRect.return_value = (100, 100, 1100, 800) # 1000x700 window
    
    # Run workflow
    result = secure_whatsapp_workflow()
    
    # Checks
    print(f"Result: {result}")
    
    # Check Relative Click
    # Expected X = 100 + 1000*0.15 = 250
    # Expected Y = 100 + 700*0.12 = 184
    sys.modules['pyautogui'].click.assert_called_with(250, 184)
    print(f"[PASS] Clicked relative coordinates: {sys.modules['pyautogui'].click.call_args}")
    
    # Check Input Verification
    # Should have typed 'a' and backspace
    calls = sys.modules['pyautogui'].method_calls
    write_calls = [c for c in calls if c[0] == 'write' and c[1][0] == 'a']
    press_calls = [c for c in calls if c[0] == 'press' and c[1][0] == 'backspace']
    
    if write_calls and press_calls:
        print("[PASS] Input verification sequence executed.")
    else:
        print("[FAIL] Input verification sequence MISSING.")

    if result:
        print("[PASS] Workflow Succeeded")
    else:
        print("[FAIL] Workflow Failed unexpected")

def test_secure_workflow_focus_fail():
    print("\n--- TEST: Secure WhatsApp Workflow (Focus Fail) ---")
    
    # Mock foreground window NEVER matching
    sys.modules['win32gui'].GetForegroundWindow.return_value = 99999 # Wrong window
    
    result = secure_whatsapp_workflow()
    
    print(f"Result: {result}")
    if not result:
        print("[PASS] Workflow aborted correctly on focus failure.")
    else:
         print("[FAIL] Workflow continued despite focus failure!")

def test_outcome_verifier_chat():
    print("\n--- TEST: Outcome Verifier (Chat Check) ---")
    ov = OutcomeVerifier()
    
    # Mock WhatsApp open first
    sys.modules['win32gui'].GetForegroundWindow.return_value = 12345
    
    # Case 1: Title matches
    sys.modules['win32gui'].GetWindowText.return_value = "WhatsApp - Brother"
    res, msg = ov.verify_outcome({"type": "whatsapp_chat", "value": "Brother"})
    print(f"Case 1 (Match): {res} - {msg}")
    if res: print("[PASS] Detected Chat")
    else: print("[FAIL] Failed to detect chat")
    
    # Case 2: Title mismatch
    sys.modules['win32gui'].GetWindowText.return_value = "WhatsApp"
    res, msg = ov.verify_outcome({"type": "whatsapp_chat", "value": "Brother"})
    print(f"Case 2 (Mismatch): {res} - {msg}")
    if not res: print("[PASS] Detected Mismatch")
    else: print("[FAIL] Failed to detect mismatch")

if __name__ == "__main__":
    test_secure_workflow_success()
    test_secure_workflow_focus_fail()
    test_outcome_verifier_chat()
