from Backend.Automation import OpenApp
import time

def test_system_fallback():
    print("Testing OpenApp with system apps...")
    
    # "calculator" often fails basic AppOpener on some systems, 
    # so this tests our new fallback logic.
    print("Attempting to open 'calculator'...")
    if OpenApp("calculator"):
        print("PASS: Calculator opened (likely via fallback)")
    else:
        print("FAIL: Calculator did not open")

    print("Attempting to open 'notepad'...")
    if OpenApp("notepad"):
        print("PASS: Notepad opened")
    else:
        print("FAIL: Notepad did not open")

if __name__ == "__main__":
    test_system_fallback()
