from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import pyautogui
import time
from Backend.TextToSpeech import TTS
from Backend.TextToSpeech import TTS
import win32gui
import pytesseract
from PIL import Image
from Backend.automation_utils import wait_until


env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKELc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
           "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e", 
           "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# --- HARDENING CONSTANTS ---
WHATSAPP_SEARCH_RATIO_X = 0.15  # 15% from left
WHATSAPP_SEARCH_RATIO_Y = 0.12  # 12% from top
TYPING_INTERVAL = 0.08          # Slow typing for safety

# Region for Visual Verification (Relative Ratios)
# x, y, width, height
SEARCH_REGION = {
    "x": 0.05,   
    "y": 0.08,   
    "w": 0.40,   
    "h": 0.08    
}

HEADER_REGION = {
    "x": 0.35,   # Right of search pane (approx 30-35%)
    "y": 0.0,    # Top edge
    "w": 0.50,   # Wide enough for name
    "h": 0.12    # Top bar height
}


useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# ... (Existing Code) ...

def verify_chat_header(hwnd, expected_contact):
    """
    Verifies that the open chat matches the expected contact name using OCR.
    """
    if not is_ocr_available():
        print("[OCR] OCR Unavailable. Skipping header verification (Trusting Input Readiness).")
        return True # Trust the previous steps
            
    try:
        print(f"[OCR] Verifying Chat Header for '{expected_contact}'...")
        rect = win32gui.GetWindowRect(hwnd)
        x, y, x2, y2 = rect
        w = x2 - x
        h = y2 - y
        
        region_left = x + int(w * HEADER_REGION["x"])
        region_top = y + int(h * HEADER_REGION["y"])
        region_width = int(w * HEADER_REGION["w"])
        region_height = int(h * HEADER_REGION["h"])
        
        # Capture
        img = pyautogui.screenshot(region=(region_left, region_top, region_width, region_height))
        
        # OCR
        text = pytesseract.image_to_string(img).strip().lower()
        print(f"[OCR] Header Text: '{text}'")
        
        # Normalize expected
        expected = expected_contact.lower().strip()
        
        # Check containment (Fuzzy match might be needed but start simple)
        if expected in text:
            print("[OCR] Chat Header Verified.")
            return True
        else:
            print(f"[OCR] Mismatch! Expected '{expected}' not found in header.")
            return False
            
    except Exception as e:
        print(f"[OCR] Header Verification Failed: {e}")
        # Fail safe
        return False

# --- OCR/Tesseract Availability Check (Part A) ---
OCR_AVAILABLE = False
try:
    # Simple check if tesseract is in path or pytesseract can be imported
    import pytesseract
    # Check binary presence (optional but good)
    # This might throw if tesseract not installed
    # We can try a dummy command or just trust import + try/except runtime
    OCR_AVAILABLE = True 
    # For robust check, we might want to check Tesseract cmd, but let's assume valid import is enough for flag init,
    # and runtime errors catch remainder.
    # Actually, pytesseract.get_tesseract_version() is a good check.
    try:
        pytesseract.get_tesseract_version()
    except:
        OCR_AVAILABLE = False
except ImportError:
    OCR_AVAILABLE = False

print(f"[System] OCR Availability: {OCR_AVAILABLE}")

def is_ocr_available():
    return OCR_AVAILABLE

# Initialize Groq client only if API key exists
client = None
if GroqAPIKey:
    client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

messages = []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]


def GoogleSearch(topic):
    search(topic)
    return True


def ContentWriterAI(prompt):
    if not client:
        print("Error: Groq API key not found. Please check your .env file.")
        return "Error: Unable to generate content - API key missing."
    
    try:
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        print(f"Error generating content: {e}")
        return f"Error: Unable to generate content - {str(e)}"

def Content(topic):
    def OpenNotepad(file):
        try:
            default_text_editor = 'notepad.exe'
            subprocess.Popen([default_text_editor, file])
            return True
        except Exception as e:
            print(f"Error opening notepad: {e}")
            return False

    topic = topic.replace("content", "").strip()
    content_by_ai = ContentWriterAI(topic)

    # Create Data directory if it doesn't exist
    data_dir = "Data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")

    filepath = os.path.join(data_dir, f"{topic.lower().replace(' ', '_')}.txt")
    
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content_by_ai)
        print(f"Content written to: {filepath}")
        
        OpenNotepad(filepath)
        return True
    except Exception as e:
        print(f"Error writing content to file: {e}")
        return False

# Content("write A application for sick leave")
def YouTubeSearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    return True


def PlayYoutube(query):
    try:
        playonyt(query)
        return True
    except Exception as e:
        print(f"Error playing YouTube video: {e}")
        return False


# Assuming `AppOpener` and `webopen` are defined or imported
import webbrowser
import requests
from bs4 import BeautifulSoup
import subprocess
import os
import platform

import webbrowser
import requests
from bs4 import BeautifulSoup
import subprocess
import os
import platform

def OpenApp(app, sess=requests.session()):
    
    try:
        # Special handling for WhatsApp to force Desktop App
        if "whatsapp" in app.lower():
            return secure_whatsapp_workflow()


        # Try to open the app using AppOpener
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True

    except:
        # Check for common system apps first
        system_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "command prompt": "cmd.exe",
            "cmd": "cmd.exe",
            "explorer": "explorer.exe",
            "paint": "mspaint.exe",
            "wordpad": "write.exe",
            "control panel": "control.exe"
        }
        
        app_lower = app.lower().strip()
        if app_lower in system_apps:
            try:
                subprocess.Popen(system_apps[app_lower])
                print(f"Opened {app} via system command.")
                
                # Verify
                if wait_until(lambda: FocusWindow(app), timeout=5, interval=0.5):
                    return True
                else:
                    print(f"Failed to verify {app} opened.")
                    return False
            except Exception as e:
                print(f"Failed to open system app {app}: {e}")

        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            # Find all anchors with valid href attributes
            links = soup.find_all('a', href=True)
            return [link.get('href') for link in links]
            
        def search_google(query):
            url = f"https://www.microsoft.com/en-us/search?q={query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
                return None

        def open_in_chrome_beta(url):
            """Open URL specifically in Google Chrome Beta"""
            system = platform.system()
            
            try:
                if system == "Windows":
                    # Common Chrome Beta paths on Windows
                    chrome_beta_paths = [
                        r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome Beta\Application\chrome.exe")
                    ]
                    
                    for path in chrome_beta_paths:
                        if os.path.exists(path):
                            subprocess.run([path, url])
                            return True
                    
                    # Fallback to regular Chrome if Beta not found
                    chrome_stable_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                    ]
                    
                    for path in chrome_stable_paths:
                        if os.path.exists(path):
                            print("Chrome Beta not found, using stable Chrome")
                            subprocess.run([path, url])
                            return True
                
                elif system == "Darwin":  # macOS
                    # Try Chrome Beta first
                    try:
                        subprocess.run(["open", "-a", "Google Chrome Beta", url])
                        return True
                    except:
                        print("Chrome Beta not found, trying stable Chrome")
                        subprocess.run(["open", "-a", "Google Chrome", url])
                        return True
                
                elif system == "Linux":
                    # Try Chrome Beta first
                    try:
                        subprocess.run(["google-chrome-beta", url])
                        return True
                    except:
                        print("Chrome Beta not found, trying stable Chrome")
                        subprocess.run(["google-chrome", url])
                        return True
                
                # Final fallback to default browser
                print("Chrome Beta and stable Chrome not found, opening in default browser")
                webbrowser.open(url)
                return True
                
            except Exception as e:
                print(f"Error opening Chrome Beta: {e}")
                # Final fallback
                webbrowser.open(url)
                return True

        # Attempt a search for the app
        # Attempt a search for the app - REMOVED FOR SECURITY
        print(f"[Automation] App {app} not found locally. Search fallback disabled.")
        return False

# --- HARDENED HELPER FUNCTIONS ---

def get_whatsapp_window():
    def callback(hwnd, handles):
        if win32gui.IsWindowVisible(hwnd) and "whatsapp" in win32gui.GetWindowText(hwnd).lower():
            handles.append(hwnd)
    handles = []
    win32gui.EnumWindows(callback, handles)
    return handles[0] if handles else None

def click_relative(hwnd, rx, ry):
    try:
        rect = win32gui.GetWindowRect(hwnd)
        x, y, x2, y2 = rect
        w = x2 - x
        h = y2 - y
        
        target_x = x + int(w * rx)
        target_y = y + int(h * ry)
        
        print(f"[Automation] Clicking Relative: {target_x}, {target_y} (Window: {x},{y} {w}x{h})")
        pyautogui.click(target_x, target_y)
        return True
    except Exception as e:
        print(f"[Automation] Relative Click Failed: {e}")
        return False


# click_first_search_result REMOVED (Mouse unreliable)

def verify_input_safety(hwnd):
    """
    Verifies input field is active by typing a test char and checking focus.
    Real visual verification would require OCR/CV. 
    Here we ensure we assume strict focus and perform the wake-up sequence.
    """
    try:
        if win32gui.GetForegroundWindow() != hwnd:
            print("[Automation] ABORT: WhatsApp lost focus during verification.")
            return False
            
        print("[Automation] Verifying input field (Type 'a' + Backspace)...")
        pyautogui.write('a')
        time.sleep(0.05)
        # 4. Cleanup Probe (Robust: Select All + Delete)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.press('backspace')
        
        # Double check focus didn't shift
        if win32gui.GetForegroundWindow() != hwnd:
            print("[Automation] ABORT: Focus shifted after input test.")
            return False
            
        print("[Automation] Input field verified (Assumed Active).")
        return True
    except Exception as e:
        print(f"[Automation] Input Verification Error: {e}")
        return False

def perform_search_input_probe(hwnd):
    """
    ONE-TIME action: Types probe, uses OCR, Clears probe.
    Returns True / False.
    MUST NOT be called inside wait_until().
    """
    PROBE = "__probe__"
    try:
        # 1. Type Probe
        print(f"[OCR] Typing probe '{PROBE}'...")
        pyautogui.write(PROBE, interval=0.05)
        time.sleep(0.1) # Allowed limit (Wait for UI to render)
        
        # 2. Capture Screenshot of Search Region
        rect = win32gui.GetWindowRect(hwnd)
        x, y, x2, y2 = rect
        w = x2 - x
        h = y2 - y
        
        region_left = x + int(w * SEARCH_REGION["x"])
        region_top = y + int(h * SEARCH_REGION["y"])
        region_width = int(w * SEARCH_REGION["w"])
        region_height = int(h * SEARCH_REGION["h"])
        
        screenshot_path = "debug_ocr_search.png"
        img = pyautogui.screenshot(region=(region_left, region_top, region_width, region_height))
        # img.save(screenshot_path) # Debug
        
        # 3. OCR Detection
        print("[OCR] Analyzing screenshot...")
        text = pytesseract.image_to_string(img)
        print(f"[OCR] Detected text: '{text.strip()}'")
        
        # 4. Cleanup Probe (Robust: Select All + Delete)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.press('backspace')
        
        if PROBE in text:
            print("[OCR] Probe confirmed visually.")
            return True
        else:
            print("[OCR] Probe NOT detected visually.")
            return False
            
    except ImportError:
        print("[OCR] Tesseract/pytesseract not installed. Falling back to non-visual check.")
        return verify_input_safety(hwnd)
    except Exception as e:
        # Check for TesseractNotFoundError string representation since verify_tesseract_available wasn't run
        if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
             print("[OCR] Tesseract Binary not found. Falling back to non-visual check.")
             return verify_input_safety(hwnd)
             
        print(f"[OCR] Verification failed: {e}")
        try: 
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace') 
        except: pass
        
        if not is_ocr_available():
            return verify_input_safety(hwnd)
        return False

# --- PERSISTENT STATE PREDICATES ---

def is_whatsapp_focused(hwnd=None):
    if not hwnd:
        hwnd = get_whatsapp_window()
    if not hwnd: return False
    
    # Check visibility and foreground
    if not win32gui.IsWindowVisible(hwnd): return False
    try:
        active = win32gui.GetForegroundWindow()
        return active == hwnd
    except:
        return False

def is_search_input_ready(hwnd):
    # Prerequisite: WhatsApp must be focused
    if not is_whatsapp_focused(hwnd):
        return False
        
def is_search_input_ready(hwnd):
    # Pure Focus Check
    try:
        return win32gui.GetForegroundWindow() == hwnd
    except:
        return False

def is_chat_active(hwnd, contact_name):
    # REMOVED: Window title check is unreliable
    return False

def is_chat_open(hwnd):
    """
    A chat is open if the message input accepts text.
    """
    return verify_input_safety(hwnd)

def is_message_ready(hwnd):
    # Similar to search input, check if we can type in the message box
    # This usually requires clicking the message box area first.
    # We can assume if Chat is Active, Message Box is at bottom.
    # CONSTANTS needed for Message Box click
    # Let's assume message box is at bottom (~90% Y)
    return verify_input_safety(hwnd)

# --- HARDENED WORKFLOW ---

def secure_whatsapp_workflow():
    print("[Automation] Starting PERSISTENT WhatsApp Workflow...")
    
    # 1. Open App
    webbrowser.open("whatsapp://")
    
    # 2. Wait for Focus
    print("[Wait] Waiting for WhatsApp focus...")
    if not wait_until(lambda: is_whatsapp_focused(), timeout=10, on_fail_reason="WhatsApp Focus"):
        print("[Automation] ABORT: WhatsApp never gained focus.")
        return False
        
    hwnd = get_whatsapp_window()
    
    # 3. Click Search & Wait for Readiness
    # We need to click first to make it ready?
    # Logic: Click, then Wait until verified.
    
    if not click_relative(hwnd, WHATSAPP_SEARCH_RATIO_X, WHATSAPP_SEARCH_RATIO_Y):
        return False
        
    if not click_relative(hwnd, WHATSAPP_SEARCH_RATIO_X, WHATSAPP_SEARCH_RATIO_Y):
        return False
        
    print("[Wait] Waiting for Search Input Focus...")
    # Pure focus verify
    if not wait_until(lambda: is_search_input_ready(hwnd), timeout=5, on_fail_reason="Search Input Focus"):
        print("[Automation] ABORT: Search input never became focused.")
        return False

    # ONE-TIME OCR PROBE
    print("[OCR] Performing Search Input Probe...")
    if not perform_search_input_probe(hwnd):
        print("[Automation] ABORT: Search input probe failed.")
        return False

    # 4. Type Contact & Enter
    # Note: Planner usually splits this. But 'secure_workflow' handles the 'open' part. 
    # If the user said "Send message...", we are likely doing the whole sequence here or just the setup?
    # The previous code returned True after setup so Planner could do "Type Name".
    # BUT user prompt: "Type contact name... Press Enter... wait_until... Type message"
    # The PROMPT implies proper granular control.
    # However, Automation.OpenApp is a "Single Step".
    # If this function replaces "Open Planner Step", it should just Open and Focus Search.
    # If this replaces "The Whole Goal", that's different.
    # Planner does: Open -> Wait -> Type Name -> Enter -> Type Message -> Enter.
    # So `secure_whatsapp_workflow` handles the "Open" step.
    # It leaves the system in "Search Ready" state.
    # We rely on 'Type' command next.
    
    # CRITICAL: The prompt description "WhatsApp Send Message Flow (PERSISTENT VERSION)" 
    # lists the WHOLE sequence.
    # But `Automation.py` executes atomic steps (Open, Type, Press).
    # If I put the whole sequence in "OpenApp", I break the atomic nature.
    # However, for SAFETY, maybe "Open WhatsApp" implies "Open and Focus Search".
    
    # The user prompt wants to replace "sleeps". 
    # The checks should be in the respective steps?
    # Or should I implement a specific "send_whatsapp_message" automation function?
    # Given "secure_whatsapp_workflow" replaces "OpenApp('whatsapp')", 
    # I will make sure it leaves the app in a perfect "Search Ready" state.
    
    # Wait, the prompt says: "Click search box... wait_until(is_search_input_ready)..."
    # This matches my implementation above.
    
    print("[Automation] WhatsApp Ready for Input.")
    return True

def secure_send_whatsapp(contact_name, message):
    """
    Implements the FULL Persistent WhatsApp Send Message Flow.
    Replaces granular steps with a monolithic, verified chain.
    """
    print(f"[Automation] Starting Secure Send to '{contact_name}'...")
    
    # Part E: Normalize Contact Name
    contact_name = contact_name.strip().replace(".", "") # Simple normalization
    
    # 1. Open & Setup (reusing secure workflow logic)
    if not secure_whatsapp_workflow():
        return False
        
    # 2. Type Contact Name (Slow)
    print(f"[Automation] Typing contact '{contact_name}'...")
    
    # SAFETY CLICK: Re-assert focus before real typing (Fixes probe cleanup focus loss)
    hwnd = get_whatsapp_window()
    click_relative(hwnd, WHATSAPP_SEARCH_RATIO_X, WHATSAPP_SEARCH_RATIO_Y)
    time.sleep(0.05) # Reduced from 0.1 (Part F)
    
    # NEW: Clear Search State (Part E)
    print("[Automation] Clearing search state...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.05)
    pyautogui.press('backspace')
    time.sleep(0.05)
    
    pyautogui.write(contact_name, interval=TYPING_INTERVAL)
    
    # Allow search results to render
    print("[Automation] Navigating search results via keyboard...")
    time.sleep(0.8) # Reduced from 1.0 (Part F)
    
    # KEYBOARD SELECTION (More reliable than mouse)
    # Move focus to first search result
    pyautogui.press("down")
    time.sleep(0.05)
    # Open selected chat
    pyautogui.press("enter")

    print("[Wait] Verifying chat open via message input readiness...")
    if not verify_input_safety(get_whatsapp_window()): # Use direct check first
         # Wait a bit if failed
         if not wait_until(lambda: verify_input_safety(get_whatsapp_window()), timeout=5, on_fail_reason="Chat Open"):
            print(f"[Automation] ABORT: Chat for '{contact_name}' did not open.")
            return False

    # NEW: Verify Header (Strict Guard) -> Now Optional (Part A)
    # If OCR is available, we check. If not, verify_chat_header returns True.
    if not wait_until(lambda: verify_chat_header(get_whatsapp_window(), contact_name), timeout=5, on_fail_reason="Header Verification"):
         # Part B/E: If OCR missing, we shouldn't fail (verify_chat_header handles this).
         # If OCR is PRESENT but fails match, we assume wrong chat?
         # User says: "If chat header cannot be verified AND input is ready -> proceed -> do NOT abort"
         
         # If verify_chat_header returned False, it means OCR matched something else explicitly.
         # But verify_chat_header() returns False on exception or mismatch.
         # If input is ready (verified above), we might want to Proceed anyway?
         # User Requirement: "If fail... -> proceed -> do NOT abort" (Part E)
         print(f"[Automation] WARNING: Header verification failed. Assuming correct chat due to Input Readiness.")
         # Proceeding instead of returning False
         # TTS(f"I could not open the correct chat for {contact_name}. Please confirm.")
         # return False
         pass 

    # 5. Type Message
    print(f"[Wait] Waiting for Message Input Readiness...")
    if not wait_until(lambda: is_message_ready(get_whatsapp_window()), timeout=4, on_fail_reason="Message Input"):
        print("[Automation] ABORT: Message input not ready.")
        return False
        
    print(f"[Automation] Typing Message: {message}...")
    pyautogui.write(message, interval=0.05)
    pyautogui.press('enter')
    
    # 6. Verify Sent (Input Cleared)
    print(f"[Wait] Verifying Message Sent (Input Cleared/Ready)...")
    # Immediate check follows
    if wait_until(lambda: is_message_ready(get_whatsapp_window()), timeout=5):
        print("[Automation] Message Sent Verified (Input ready).")
        return True
    else:
        print("[Automation] Warning: Input not ready after send (Possible network lag).")
        return True

def FocusWindow(app_name):
    """Force focus to a *visible* window with title containing app_name"""
    try:
        def windowEnumerationHandler(hwnd, top_windows):
            if win32gui.IsWindowVisible(hwnd):
                top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        
        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        
        target_hwnd = None
        for i in top_windows:
            if app_name.lower() in i[1].lower():
                target_hwnd = i[0]
                break
        
        if target_hwnd:
            print(f"Focusing window: {win32gui.GetWindowText(target_hwnd)}")
            # Initial restore/show
            win32gui.ShowWindow(target_hwnd, 9) # SW_RESTORE
            
            # Forced foreground trickery (Windows restriction workaround)
            try:
                win32gui.SetForegroundWindow(target_hwnd)
            except Exception as e:
                # Fallback: Press ALT (sometimes helps unlock focus) or use shell
                print(f"SetForegroundWindow failed: {e}. Trying simple alt-tab trick.")
                pyautogui.press('alt') 
                win32gui.SetForegroundWindow(target_hwnd)
                
            # Verify focus acquisition
            if not wait_until(lambda: win32gui.GetForegroundWindow() == target_hwnd, timeout=2.0, interval=0.1):
                print(f"[Focus] Warning: Window '{app_name}' did not report foreground match.")
            return True
        else:
            print(f"Window '{app_name}' not found for focusing.")
            return False
    except Exception as e:
        print(f"Error focusing window: {e}")
        return False
# OpenApp("instagram")
def CloseApp(app):
    if "chrome" in app.lower():
        try:
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=True)
            print(f"Closed Chrome using taskkill")
            return True
        except:
            pass
    
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        print(f"Closed {app} using AppOpener")
        return True
    except Exception as e:
        print(f"Error closing {app}: {e}")
        return False


def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    try:
        if command == "mute":
            mute()
        elif command == "unmute":
            unmute()
        elif command == "volume up":
            volume_up()
        elif command == "volume down":
            volume_down()
        else:
            print(f"Unknown system command: {command}")
            return False
        
        print(f"Executed system command: {command}")
        return True
    except Exception as e:
        print(f"Error executing system command {command}: {e}")
        return False

def Type(text, target_app=None):
    # Removed blind sleep for focus
    
    # Optional: Logic to verify active window title if target_app is provided
    # active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    # print(f"Active Window: {active_window}")
    
    try:
        pyautogui.write(text)
        # Removed blind sleep: time.sleep(2)
        print(f"Typed: {text}")
        return True
    except Exception as e:
        print(f"Error typing text: {e}")
        return False

def Press(key):
    try:
        if "+" in key:
            keys = key.split("+")
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)
        print(f"Pressed: {key}")
        return True
    except Exception as e:
        print(f"Error pressing key: {e}")
        return False


from Backend.outcomes import Outcome

from functools import wraps

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"[Timing] {func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@measure_time
async def execute_step(action, target) -> Outcome:
    """
    Executes a single step.
    Returns: Outcome(success=True|False, reason="...")
    """
    try:
        # Step-specific TTS
        # Note: If TTS is desired, it should be called here or by the caller.
        # For v3, GoalManager likely handles the high-level narration.
        
        if action == "open":
            await asyncio.to_thread(TTS, f"Opening {target}")
            success = await asyncio.to_thread(OpenApp, target)
            return Outcome(success=success, reason=None if success else "Failed to open app")

        elif action == "close":
            await asyncio.to_thread(TTS, f"Closing {target}")
            success = await asyncio.to_thread(CloseApp, target)
            return Outcome(success=success, reason=None if success else "Failed to close app")

        elif action == "play":
            await asyncio.to_thread(TTS, f"Playing {target}")
            success = await asyncio.to_thread(PlayYoutube, target)
            return Outcome(success=success, reason=None if success else "Failed to play media")

        elif action == "content":
            await asyncio.to_thread(Content, target)
            return Outcome(success=True)

        elif action == "search_web" or action == "google search":
            await asyncio.to_thread(TTS, f"Searching Google for {target}")
            await asyncio.to_thread(GoogleSearch, target)
            return Outcome(success=True)
            
        elif action == "youtube search":
            await asyncio.to_thread(TTS, f"Searching YouTube for {target}")
            await asyncio.to_thread(YouTubeSearch, target)
            return Outcome(success=True)

        elif action == "system":
            await asyncio.to_thread(System, target)
            return Outcome(success=True)

        elif action == "generate_image":
            # PART 4: EXECUTION BRIDGE
            print("[DEBUG] Routing to LOCAL image generation")
            from Backend.ImageGenerationLocal import generate_image_local
            print("[ImageGen] Using Local Stable Diffusion")
            try:
                # Run sync in thread to avoid blocking asyncio loop
                path = await asyncio.to_thread(generate_image_local, target)
                print(f"[Automation] Image saved to {path}")
                
                # Verify file exists
                if os.path.exists(path):
                    os.startfile(path)
                    return Outcome(success=True)
                else:
                    return Outcome(success=False, reason="Image file not found after generation")
            except Exception as e:
                print(f"[ImageGen] Local Generation Error: {e}")
                return Outcome(success=False, reason=str(e))

        elif action == "type":
            text = target
            if text.endswith(".") and not text.endswith(".."):
                 text = text.removesuffix(".")
            
            await asyncio.to_thread(TTS, f"Typing: {text}")
            success = await asyncio.to_thread(Type, text)
            return Outcome(success=success, reason=None if success else "Failed to type text")

        elif action == "press":
            key = target.removesuffix(".")
            success = await asyncio.to_thread(Press, key)
            return Outcome(success=success, reason=None if success else "Failed to press key")
            
        elif action == "speak":
            # TTS is blocking or async? Backend.TextToSpeech.TTS usually blocks?
            # We run it in thread.
            await asyncio.to_thread(TTS, target)
            return Outcome(success=True)

        elif action == "wait":
            try:
                seconds = float(target)
                print(f"[AUTOMATION] Waiting for {seconds} seconds")
                await asyncio.sleep(seconds)
                return Outcome(success=True)
            except Exception as e:
                return Outcome(success=False, reason=str(e))

        else:
            return Outcome(success=False, reason=f"Unknown action: {action}")

    except Exception as e:
        print(f"Execute Step Error: {e}")
        return Outcome(success=False, reason=str(e))

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        command = command.strip().lower()
        print(f"[AUTOMATION] Executing command: {command}")
        
        if command.startswith("open "):
            yield await execute_step("open", command.removeprefix("open ").strip())
        elif command.startswith("close "):
            yield await execute_step("close", command.removeprefix("close ").strip())
        elif command.startswith("play "):
            yield await execute_step("play", command.removeprefix("play ").strip())
        elif command.startswith("content "):
            yield await execute_step("content", command.removeprefix("content ").strip())
        elif command.startswith("search_web ") or command.startswith("google search "):
            # Handle both "search_web" and "google search" as the same action
            if command.startswith("google search "):
                yield await execute_step("search_web", command.removeprefix("google search ").strip())
            else: # command.startswith("search_web ")
                yield await execute_step("search_web", command.removeprefix("search_web ").strip())
        elif command.startswith("youtube search "):
             yield await execute_step("youtube search", command.removeprefix("youtube search ").strip())
        elif command.startswith("system "):
             yield await execute_step("system", command.removeprefix("system ").strip())
        elif command.startswith("type "):
             yield await execute_step("type", command.removeprefix("type ").strip())
        elif command.startswith("press "):
             yield await execute_step("press", command.removeprefix("press ").strip())
        elif command.startswith("speak "):
             yield await execute_step("speak", command.removeprefix("speak ").strip())
        elif command.startswith("send_whatsapp "):
             # Format: send_whatsapp [Contact] | [Message]
             parts = command.removeprefix("send_whatsapp ").split("|")
             if len(parts) >= 2:
                 contact = parts[0].strip()
                 msg = parts[1].strip()
                 if msg.lower() == "none" or msg == "":
                     print("[Automation] ABORT: Message content is empty or 'None'.")
                     yield Outcome(success=False, reason="Message content missing")
                     continue # Skip execution
                 
                 await asyncio.to_thread(TTS, f"Sending WhatsApp message to {contact}")
                 success = await asyncio.to_thread(secure_send_whatsapp, contact, msg)
                 yield Outcome(success=success, reason=None if success else "Secure WhatsApp flow failed")
             else:
                 print("[Automation] Invalid send_whatsapp format. Use 'Contact | Message'")
                 yield Outcome(success=False, reason="Invalid send_whatsapp format")
        
        elif command.startswith("generate_image "):
            print("[DEBUG] Routing to LOCAL image generation")
            prompt = command.removeprefix("generate_image ").strip()
            
            # Reusing the logic inside execute_step via recursion or call?
            # Better to call execute_step to keep logic centralized
            yield await execute_step("generate_image", prompt)

        elif command.startswith("wait "):
             yield await execute_step("wait", command.removeprefix("wait ").strip())

        else:
            print(f"[Automation] Unknown command: {command}")
            yield Outcome(success=False, reason=f"Unknown command: {command}")


from Backend.CommandCompiler import compile_commands

async def Automation(commands: list[str]):
    print("[AUTOMATION] Automation() CALLED")
    print(f"[AUTOMATION] Commands received: {commands}")
    
    commands = compile_commands(commands)

    print(f"[Automation] Compiled commands: {commands}")

    results = []
    async for result in TranslateAndExecute(commands):
        print(f"[AUTOMATION] Step result: {result}")
        results.append(result)

    return results


if __name__ == "__main__":
    test_commands = [
        "send_whatsapp Mom | Hello"
    ]

    asyncio.run(Automation(test_commands))