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
# We mocked rich, so 'from rich import print' will import a MagicMock
# But we need that mock to actually record calls so we can inspect them.

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
sys.modules['Backend.WebSearch'] = MagicMock()
sys.modules['Backend.SpeechEngine'] = MagicMock()
sys.modules['Backend.KeyboardEngine'] = MagicMock()

sys.path.append(os.getcwd())

# We need to setup 'rich.print' BEFORE importing Automation
# Since we mocked sys.modules['rich'], we can configure it.
mock_rich = sys.modules['rich']
mock_print = MagicMock()
mock_rich.print = mock_print

try:
    import Backend.Automation
    # Force re-import or update the print if it was already imported (it wasn't since we mocked modules first)
    # But wait, 'from rich import print' makes 'print' a name in Automation namespace.
    # It will point to mock_rich.print.
    from Backend.Automation import Automation
except Exception as e:
    with open("compiler_log.txt", "w") as f:
        f.write(f"FAIL_IMPORT: {e}\n")
    sys.exit(1)

async def run_test():
    with open("compiler_verify.log", "w") as f:
        f.write("--- Starting Compiler Verification ---\n")
        
        # Configure ImageGen Local
        mock_local_module = sys.modules['Backend.ImageGenerationLocal']
        mock_gen_func = MagicMock(return_value="C:\\fake\\path\\image.png")
        mock_local_module.generate_image_local = mock_gen_func

        # Test Case: "Generate an image of flower"
        raw_commands = ["Generate an image of flower"]
        
        with patch('os.startfile') as mock_startfile:
            try:
                 await Automation(raw_commands)
            except Exception as e:
                f.write(f"FAIL_EXEC: {e}\n")

        # Now examine what was printed
        # mock_print.call_args_list holds all calls
        for call in mock_print.call_args_list:
            # call.args[0] should be the string
            args, _ = call
            if args:
                f.write(f"{str(args[0])}\n")

if __name__ == "__main__":
    asyncio.run(run_test())
