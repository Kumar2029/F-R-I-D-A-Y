from Backend.TextToSpeech import TTS
try:
    TTS("This is a text to speech test")
except Exception as e:
    print(f"Test Failed: {e}")
