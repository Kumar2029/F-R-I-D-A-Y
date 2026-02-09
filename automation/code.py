from Backend.Automation import OpenApp, Type, Press
from Backend.TextToSpeech import TTS
from core.intents import CodeIntent
import time

def handle_code_automation(intent: CodeIntent):
    print(f"[Action] Executing CODE Domain: {intent.task} -> {intent.filename}")
    
    # 1. Open VS Code
    OpenApp("visual studio code")
    # Wait for window focus (rudimentary wait)
    time.sleep(3) 

    # 2. New File
    Press("ctrl+n")
    time.sleep(0.5)
    
    # 3. Write Code (Strict from Intent)
    Type(intent.generated_code)
    time.sleep(0.5)

    # 4. Save File
    Press("ctrl+s")
    time.sleep(1)
    Type(intent.filename)
    Press("enter")
    time.sleep(1)
    
    # 5. Run Code (Terminal)
    Press("ctrl+`") # Open terminal
    time.sleep(1)
    Type(f"python {intent.filename}")
    Press("enter")

    TTS(f"Code for {intent.task} written and executed.")
    return True
