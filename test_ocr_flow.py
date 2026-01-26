
import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())

# Import module
from Backend import Automation

@patch('Backend.Automation.win32gui')
@patch('Backend.Automation.pyautogui')
@patch('Backend.Automation.pytesseract')
@patch('Backend.Automation.Image')
def test_ocr_verification(mock_img, mock_tess, mock_gui, mock_win32):
    print("\n--- TEST: OCR Verification Logic (Patched) ---")
    
    # Setup Mocks
    mock_win32.GetWindowRect.return_value = (0, 0, 1000, 1000)
    mock_win32.GetForegroundWindow.return_value = 12345
    
    # 1. Test SUCCESS Case (Probe Found)
    print("\n[Case 1] Tesseract finds probe text")
    mock_tess.image_to_string.return_value = "Some text __probe__ found"
    
    res = Automation.perform_search_input_probe(12345)
    print(f"Result: {res}")
    if res:
        print("[PASS] OCR confirmed active input")
        mock_tess.image_to_string.assert_called()
    else:
        print("[FAIL] OCR failed to confirm active input")

    # 2. Test FAIL Case (Probe Not Found)
    print("\n[Case 2] Tesseract does not find probe")
    mock_tess.image_to_string.return_value = "Random text"
    
    res = Automation.perform_search_input_probe(12345)
    print(f"Result: {res}")
    if not res:
        print("[PASS] OCR correctly rejected inactive input")
    else:
        print("[FAIL] OCR falsely confirmed inactive input")

    # 3. Test FALLBACK Case (Exception)
    print("\n[Case 3] Tesseract Exception (Fallback)")
    mock_tess.image_to_string.side_effect = Exception("tesseract is not installed")
    
    with patch('Backend.Automation.verify_input_safety', return_value="FALLBACK_CALLED") as mock_fallback:
        res = Automation.perform_search_input_probe(12345)
        print(f"Result: {res}")
        if res == "FALLBACK_CALLED":
             print("[PASS] Fallback to verify_input_safety occurred")
        else:
             print("[FAIL] Result was not fallback")

if __name__ == "__main__":
    test_ocr_verification()
