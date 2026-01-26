from AppOpener import open as appopen
import subprocess

def test_open():
    print("Testing AppOpener...")
    try:
        appopen("notepad", match_closest=True, output=True, throw_error=True)
        print("Successfully opened notepad via AppOpener")
    except Exception as e:
        print(f"AppOpener failed: {e}")
        
    print("Testing subprocess...")
    try:
        subprocess.Popen("notepad.exe")
        print("Successfully opened notepad via subprocess")
    except Exception as e:
        print(f"Subprocess failed: {e}")

if __name__ == "__main__":
    test_open()
