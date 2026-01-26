
import win32gui
import time
import pyautogui
import webbrowser

def list_windows():
    print("\nListing Visible Windows:")
    def handler(hwnd, tops):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                tops.append(title)
    
    titles = []
    win32gui.EnumWindows(handler, titles)
    for t in titles:
        print(f" - {t}")
    return titles

def test_focus_and_type():
    print("\n--- TEST: WhatsApp Focus & Type ---")
    print("Opening WhatsApp...")
    webbrowser.open("whatsapp://")
    time.sleep(3)
    
    titles = list_windows()
    whatsapp_titles = [t for t in titles if "whatsapp" in t.lower()]
    
    print(f"\nFound WhatsApp Windows: {whatsapp_titles}")
    
    if not whatsapp_titles:
        print("ERROR: WhatsApp window not found in list.")
        return

    target = whatsapp_titles[0]
    print(f"Attempting to focus: '{target}'")
    
    hwnd = win32gui.FindWindow(None, target)
    if hwnd:
        try:
            # Try to force focus
            win32gui.ShowWindow(hwnd, 9) # Restore
            win32gui.SetForegroundWindow(hwnd)
            print("SetForegroundWindow called.")
            time.sleep(1)
            
            print("Typing 'TEST KEYSTROKES'...")
            pyautogui.write("TEST KEYSTROKES")
            print("Typing done.")
        except Exception as e:
            print(f"Focus Error: {e}")
            # Try the ALT key trick
            print("Trying ALT key trick...")
            pyautogui.press('alt')
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(1)
            pyautogui.write("TEST KEYSTROKES (ALT TRICK)")
    else:
        print("Could not get HWND.")

if __name__ == "__main__":
    test_focus_and_type()
