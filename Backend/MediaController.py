import json
import os
import time
from rich import print
from core.intents import MediaIntent
from Backend.MediaVerifier import MediaVerifier
from Backend.TextToSpeech import TTS
# Executors will be imported dynamically or statically
# from automation import spotify, youtube_playback, local_media

class MediaController:
    def __init__(self):
        self.verifier = MediaVerifier()
        self.memory_path = "memory/media_preferences.json"
        self.calibration_path = "config/media_ui_map.json"
        self._load_memory()
        
    def _load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                self.memory = json.load(f)
        else:
            self.memory = {"history": [], "preferences": {}}

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def load_calibration(self):
        if os.path.exists(self.calibration_path):
            with open(self.calibration_path, 'r') as f:
                return json.load(f)
        return {}

    def calibrate(self):
        """
        Interactive calibration mode.
        """
        import pyautogui
        TTS("Starting Media Calibration. Please follow the instructions.")
        
        points = {}
        
        # 1. Spotify Search Bar
        TTS("Please open Spotify and hover over the search bar. I will record the position in 5 seconds.")
        time.sleep(5)
        points["spotify_search"] = pyautogui.position()
        TTS("Recorded.")
        
        # 2. Spotify First Result
        TTS("Now search for a song, and hover over the first track result. Recording in 5 seconds.")
        time.sleep(5)
        points["spotify_first_result"] = pyautogui.position()
        TTS("Recorded.")
        
        # 3. YouTube First Video
        TTS("Please open YouTube in your browser, search for something, and hover over the first video thumbnail. Recording in 5 seconds.")
        time.sleep(5)
        points["youtube_first_result"] = pyautogui.position()
        TTS("Recorded.")
        
        # Save
        os.makedirs(os.path.dirname(self.calibration_path), exist_ok=True)
        with open(self.calibration_path, 'w') as f:
            json.dump(points, f, indent=2)
            
        TTS("Calibration complete. settings saved.")
        return True

    def normalize_intent(self, raw_query: str) -> MediaIntent:
        """
        Layer 1: Intent Normalization
        Parses "Play X on Y" -> MediaIntent
        """
        raw_query = raw_query.lower().strip()
        platform = None
        song = raw_query
        
        # Simple parsing logic
        if " on " in raw_query:
            parts = raw_query.split(" on ")
            song = parts[0].replace("play", "").strip()
            platform_candidate = parts[1].strip()
            if "spotify" in platform_candidate:
                platform = "spotify"
            elif "youtube" in platform_candidate:
                platform = "youtube"
            elif "file" in platform_candidate or "local" in platform_candidate:
                platform = "local"
        else:
            song = raw_query.replace("play", "").strip()
            
        return MediaIntent(
            action="play",
            query=song,
            platform_hint=platform
        )

    def resolve_platform(self, intent: MediaIntent):
        """
        Layer 2: Platform Resolution
        Returns list of platforms to try in order.
        """
        # 1. Explicit
        if intent.platform_hint:
            return [intent.platform_hint] + self._get_fallbacks(intent.platform_hint)
            
        # 2. History (Last successful for this song?)
        # Clean query for key lookup
        key = intent.query.lower().strip()
        history = self.memory.get("history", [])
        
        # Find last entry for this song
        last_entry = next((item for item in reversed(history) if item["song"] == key), None)
        
        if last_entry:
            best = last_entry["best_platform"]
            print(f"[GMC] Found learned preference for '{key}': {best}")
            return [best] + self._get_fallbacks(best)
        
        # 3. Default Priority
        return ["spotify", "youtube", "local"]

    def _get_fallbacks(self, primary):
        defaults = ["spotify", "youtube", "local"]
        return [p for p in defaults if p != primary]

    def execute(self, intent: MediaIntent):
        """
        Orchestrates the playback.
        """
        platforms = self.resolve_platform(intent)
        print(f"[GMC] Platform Plan: {platforms}")
        
        for platform in platforms:
            print(f"[GMC] Attempting: {platform}")
            success = False
            
            if platform == "spotify":
                from automation import spotify
                success = spotify.play(intent.query, self.verifier)
            elif platform == "youtube":
                from automation import youtube_playback
                success = youtube_playback.play(intent.query, self.verifier)
            elif platform == "local":
                from automation import local_media
                success = local_media.play(intent.query, self.verifier)
                
            if success:
                print(f"[GMC] Success on {platform}")
                self._record_success(intent.query, platform)
                TTS(f"Playing {intent.query} on {platform}.")
                return True
            else:
                print(f"[GMC] Failed on {platform}. trying next.")
                time.sleep(1.0) # Grace period before switching
        
        TTS("I couldn't reliably start playback on any platform.")
        return False

    def _record_success(self, song, platform):
        # Layer 5: Learning
        try:
            entry = {
                "song": song.lower().strip(),
                "best_platform": platform,
                "timestamp": time.time()
            }
            
            # Update history
            if "history" not in self.memory:
                self.memory["history"] = []
                
            self.memory["history"].append(entry)
            
            # Keep size manageable
            if len(self.memory["history"]) > 100:
                self.memory["history"] = self.memory["history"][-100:]
                
            self._save_memory()
            print(f"[GMC] Learned: {song} -> {platform}")
        except Exception as e:
            print(f"[GMC] Learning failed: {e}")
