import pyautogui
import time
import subprocess

def test_type():
    print("Opening Notepad...")
    subprocess.Popen("notepad.exe")
    time.sleep(2) # Wait for it to open
    
    print("Typing text...")
    pyautogui.write("Hello from JARVIS Automation!", interval=0.1)
    pyautogui.press("enter")
    pyautogui.write("This text was typed automatically.")
    
    print("Test complete.")

if __name__ == "__main__":
    test_type()
