import os
import subprocess
from fuzzywuzzy import process
from Backend.MediaVerifier import MediaVerifier
from rich import print

MUSIC_DIRS = [
    os.path.expanduser("~\\Music"),
    os.path.expanduser("~\\Downloads"),
    "D:\\Music" # Example
]

MUSIC_EXTS = [".mp3", ".wav", ".flac", ".m4a"]

def find_file(query):
    candidates = []
    print(f"[Local] Searching for '{query}'...")
    
    for d in MUSIC_DIRS:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for f in files:
                if any(f.lower().endswith(ext) for ext in MUSIC_EXTS):
                    candidates.append(os.path.join(root, f))
    
    if not candidates:
        return None
        
    # Fuzzy match
    # keys are filenames, values are full paths
    choices = {os.path.basename(p): p for p in candidates}
    best_match = process.extractOne(query, list(choices.keys()))
    
    if best_match and best_match[1] > 60:
        return choices[best_match[0]]
        
    return None

def play(query: str, verifier: MediaVerifier):
    print(f"[Local] Executing Play: {query}")
    
    filepath = find_file(query)
    if not filepath:
        print("[Local] No matching file found.")
        return False
        
    print(f"[Local] Opening: {filepath}")
    os.startfile(filepath) # Windows default player
    
    # Verify?
    # Hard to verify default player name without knowing it.
    # We can check audio activity generically.
    # Or check if a new window opened? 
    
    return True
