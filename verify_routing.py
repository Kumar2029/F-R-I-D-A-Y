import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# --- Mocks ---
sys.modules['AppOpener'] = MagicMock()
sys.modules['webbrowser'] = MagicMock()
sys.modules['pywhatkit'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['bs4'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['groq'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['keyboard'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['win32gui'] = MagicMock()
sys.modules['pytesseract'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Internal
sys.modules['Backend.TextToSpeech'] = MagicMock()
sys.modules['Backend.automation_utils'] = MagicMock()
sys.modules['Backend.ImageGenerationLocal'] = MagicMock()
sys.modules['Backend.ImageGeneration'] = MagicMock()
# Explicitly mock WebSearch module and its GoogleSearch attribute
mock_websearch = MagicMock()
mock_google_search_func = MagicMock()
mock_websearch.GoogleSearch = mock_google_search_func
sys.modules['Backend.WebSearch'] = mock_websearch

sys.modules['Backend.SpeechEngine'] = MagicMock()
sys.modules['Backend.KeyboardEngine'] = MagicMock()

sys.path.append(os.getcwd())

try:
    import Backend.Automation
    from Backend.Automation import TranslateAndExecute
except Exception as e:
    print(f"FAIL_IMPORT: {e}", flush=True)
    sys.exit(1)

async def run_test():
    print("START_TEST", flush=True)
    
    # Configure ImageGen Local
    mock_local_module = sys.modules['Backend.ImageGenerationLocal']
    mock_gen_func = MagicMock(return_value="C:\\fake\\path\\image.png")
    mock_local_module.generate_image_local = mock_gen_func

    command = "generate_image A futuristic city"
    
    with patch('os.startfile') as mock_startfile:
        try:
            async for res in TranslateAndExecute([command]):
                pass
        except Exception as e:
            print(f"FAIL_EXEC: {e}", flush=True)
            return

        # Check Calls
        if mock_gen_func.called:
            print(f"PASS_GEN_CALLED: {mock_gen_func.call_args[0][0]}", flush=True)
        else:
            print("FAIL_GEN_NOT_CALLED", flush=True)

        if mock_startfile.called:
            print("PASS_STARTFILE", flush=True)
        else:
            print("FAIL_STARTFILE", flush=True)

        # Check Google Search
        # We need to check the exact object that Automation imported
        try:
            gs = Backend.Automation.GoogleSearch
            print(f"DEBUG_GS_TYPE: {type(gs)}", flush=True)
            if hasattr(gs, 'called') and gs.called:
                print("FAIL_FALLBACK_TRIGGERED", flush=True)
            else:
                print("PASS_NO_FALLBACK", flush=True)
        except Exception as e:
            print(f"FAIL_CHECK_GS: {e}", flush=True)

    # Unknown Command
    command_unk = "generate_hologram foo"
    async for res in TranslateAndExecute([command_unk]):
        pass
        
    try:
        gs = Backend.Automation.GoogleSearch
        if hasattr(gs, 'called') and gs.called:
            print("FAIL_UNK_FALLBACK", flush=True)
        else:
            print("PASS_UNK_NO_FALLBACK", flush=True)
    except:
        pass

if __name__ == "__main__":
    asyncio.run(run_test())
