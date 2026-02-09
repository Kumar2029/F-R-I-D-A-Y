from Backend.SpeechToText import SpeechRecognition

def get_user_input() -> str:
    """
    Strict Input Layer:
    1. Capture Microphone
    2. STT
    3. Normalize (handled by SpeechRecognition internal QueryModifier)
    4. Return Text
    
    Returns:
        str: Normalized text command or empty string if failed.
    """
    # Reuse existing robust STT logic
    # This function blocks until input is received
    text = SpeechRecognition()
    
    if text:
        return text.strip()
    return ""
