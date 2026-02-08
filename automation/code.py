from Backend.Automation import OpenApp, Type, Press
from Backend.TextToSpeech import TTS
import time

def generate_code(content):
    # Determine what to write based on content
    # For now, simple Hello World or placeholder
    if "python" in content.lower():
        return 'print("Hello from JARVIS Action Domain")'
    return "# Generated Code Placeholder"

def handle_code_automation(goal):
    print(f"[Action] Executing CODE Domain: {goal.content}")
    
    # 1. Open VS Code
    OpenApp("visual studio code")
    # Wait for window focus (rudimentary wait)
    time.sleep(3) 

    # 2. New File
    Press("ctrl+n")
    time.sleep(0.5)
    
    # 3. Write Code
    code = generate_code(goal.content or "")
    Type(code)
    time.sleep(0.5)

    # 4. Save File
    Press("ctrl+s")
    time.sleep(1)
    Type("program.py")
    Press("enter")
    time.sleep(1)
    
    # Opt: overwrite confirmation if needed? (Assuming clean state or Enter handles it)

    # 5. Run Code (Terminal)
    Press("ctrl+`") # Open terminal
    time.sleep(1)
    Type("python program.py")
    Press("enter")

    TTS("Code written, executed, and saved successfully.")
    return True
