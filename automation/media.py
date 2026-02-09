from Backend.Automation import OpenApp, Type, Press
from Backend.TextToSpeech import TTS
from core.intents import MediaIntent
import time

def handle_media_automation(intent: MediaIntent):
    print(f"[Action] Executing MEDIA Domain: {intent.platform} -> {intent.query}")
    
    # 1. Open App
    OpenApp(intent.platform)
    time.sleep(3) # Wait for load

    # 2. Search (Strict Steps)
    Press("ctrl+l")
    time.sleep(0.5)
    
    Type(intent.query)
    time.sleep(0.5)
    Press("enter")

    # 3. Play (Select first result)
    time.sleep(2) # Wait for results
    Press("down") # Select top result specifically
    time.sleep(0.2)
    Press("enter") # Open it
    time.sleep(1.0)
    Press("space") # Force Playback toggle

    TTS(f"Playing {intent.query} on {intent.platform}.")
    return True
