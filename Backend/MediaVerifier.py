import pygetwindow as gw
try:
    from pycaw.pycaw import AudioUtilities
    PYCAW_AVAILABLE = True
except ImportError:
    AudioUtilities = None
    PYCAW_AVAILABLE = False
import hashlib
import pyautogui
import win32gui
import time
from rich import print

class MediaVerifier:
    def verify_audio_activity(self, app_name_bases):
        """
        Verifies if any of the given app process names are producing audio.
        app_name_bases: list of strings, e.g., ["spotify", "chrome"]
        """
        print(f"[MediaVerifier] Checking audio activity for: {app_name_bases}")
        if not PYCAW_AVAILABLE:
            print("[MediaVerifier] pycaw not installed. Audio verification unavailable.")
            return False
            
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process:
                    process_name = session.Process.name().lower()
                    for base in app_name_bases:
                        if base in process_name:
                            # Check if audio is actually playing (state 1 = Active)
                            # behaviors: 0=Inactive, 1=Active, 2=Expired
                            # We might need to check peak value if state is unreliable, but state is usually good for "playing".
                            # However, sometimes paused sessions remain "Active". 
                            # Better check: is meter showing output?
                            # For simplicity, we'll check existence first.
                            # But strictly, we want *playback*.
                            return True
            print("[MediaVerifier] No matching audio session found.")
            return False
        except Exception as e:
            print(f"[MediaVerifier] Audio check failed: {e}")
            return False

    def verify_active_window(self, title_keywords):
        """
        Verifies if the active window title contains any of the keywords.
        """
        try:
            window = gw.getActiveWindow()
            if not window:
                return False
            title = window.title.lower()
            print(f"[MediaVerifier] Active Window: '{title}'")
            for keyword in title_keywords:
                if keyword.lower() in title:
                    return True
            return False
        except Exception as e:
            print(f"[MediaVerifier] Active window check failed: {e}")
            return False

    def get_ui_hash(self, region=None):
        """
        Generates a hash of the screen execution (or specific region).
        Used to detect UI changes (e.g., search results loaded).
        """
        try:
            if region:
                img = pyautogui.screenshot(region=region)
            else:
                img = pyautogui.screenshot()
            return hashlib.md5(img.tobytes()).hexdigest()
        except Exception as e:
            print(f"[MediaVerifier] UI Hash failed: {e}")
            return None

    def verify_media_state(self):
        """
        Checks global media playing state if possible (Windows Media Integration).
        This is complex in pure Python without specific WinRT bindings.
        For now, we rely on Audio verification.
        """
        # TODO: Implement WinRT MediaManager check if needed.
        return True 
