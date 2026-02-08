from Backend.SpeechToText import SpeechRecognition

def listen():
    # Wrapper for SpeechRecognition to match requested interface
    return SpeechRecognition()
