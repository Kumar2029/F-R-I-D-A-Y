from Backend.Automation import OpenApp, Type, Press
from Backend.TextToSpeech import TTS
import time

def handle_media_automation(goal):
    print(f"[Action] Executing MEDIA Domain: {goal.target}")
    
    # 1. Open Spotify
    OpenApp("spotify")
    time.sleep(3) # Wait for load

    # 2. Search
    Press("ctrl+l")
    time.sleep(0.5)
    
    query = goal.target or "popular song"
    Type(query)
    time.sleep(0.5)
    Press("enter")

    # 3. Play (Select first result)
    time.sleep(2)
    Press("enter")

    TTS("Playing song on Spotify.")
    return True
