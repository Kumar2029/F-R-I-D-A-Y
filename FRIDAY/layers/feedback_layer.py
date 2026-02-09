from Backend.TextToSpeech import TTS

class FeedbackLayer:
    """
    Handles communication with the user.
    Strictly for final outcomes or critical clarifications.
    No internal logs.
    """
    def speak(self, text: str):
        if not text:
            return
        
        # We could add specific filtering here if needed
        # e.g. removing code blocks or long file paths from being spoken
        
        print(f"[Feedback] Speaking: {text}")
        TTS(text)

    def speak_error(self, message: str):
        print(f"[Feedback] Error: {message}")
        TTS(f"I encountered an issue: {message}")
