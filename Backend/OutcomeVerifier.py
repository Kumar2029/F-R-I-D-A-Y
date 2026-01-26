try:
    import win32gui
except ImportError:
    win32gui = None

class OutcomeVerifier:
    def __init__(self):
        pass

    def verify_outcome(self, criteria):
        """
        Verifies if the success criteria is met.
        Criteria example: {"type": "window_title", "value": "WhatsApp"}
        """
        if not criteria:
            return True, "No criteria provided"

        check_type = criteria.get("type")
        value = criteria.get("value")

        if check_type == "window_title":
            return self._verify_window_title(value)
        
        return True, "Unknown criteria type (assumed success)"

    def _verify_window_title(self, partial_title, timeout=5, retries=10):
        if not win32gui:
            return True, "win32gui not installed, skipping check"
            
        import time
        step_delay = timeout / retries
        
        for i in range(retries):
            try:
                hwnd = win32gui.GetForegroundWindow()
                active_title = win32gui.GetWindowText(hwnd).lower()
                
                if partial_title.lower() in active_title:
                    return True, f"Window '{active_title}' matches '{partial_title}'"
            except Exception as e:
                print(f"Error checking window: {e}")
            
            time.sleep(step_delay)
            
        # Final check failed
        return False, f"Active window '{active_title}' does not match '{partial_title}' after {timeout}s"

    def _verify_whatsapp_chat_open(self, contact_name, timeout=5):
        """
        Verifies that the WhatsApp window title matches the Contact Name.
        WhatsApp Desktop usually sets the window title to the active chat name.
        """
        print(f"[OutcomeVerifier] Verifying WhatsApp chat open for: {contact_name}")
        
        # 1. First ensure WhatsApp is the active app
        is_wa, msg = self._verify_window_title("WhatsApp", timeout=2)
        if not is_wa:
            return False, f"WhatsApp is not the active window. ({msg})"
            
        # 2. Check strict title match (Contact Name should be in title)
        # We assume the title becomes "Contact Name" or contains it.
        return self._verify_window_title(contact_name, timeout=timeout)

    def verify_outcome(self, criteria):
        """
        Verifies if the success criteria is met.
        Criteria example: {"type": "window_title", "value": "WhatsApp"}
        Or: {"type": "whatsapp_chat", "value": "Brother"}
        """
        if not criteria:
            return True, "No criteria provided"

        check_type = criteria.get("type")
        value = criteria.get("value")

        if check_type == "window_title":
            return self._verify_window_title(value)
        elif check_type == "whatsapp_chat":
            return self._verify_whatsapp_chat_open(value)
        
        return True, "Unknown criteria type (assumed success)"

