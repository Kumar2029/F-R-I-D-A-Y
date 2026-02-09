import sys
import os
import shutil

# Ensure root is in path
sys.path.append(os.getcwd())

from FRIDAY.layers.learning_layer import LearningAdvisoryLayer
from FRIDAY.core.models import Intent, ActionDomain

# Clean memory for test
MEM_DIR = os.path.join("FRIDAY", "memory")
if os.path.exists(MEM_DIR):
    shutil.rmtree(MEM_DIR)

print("--- TESTING LEARNING LAYER ---")

learning = LearningAdvisoryLayer()

# Test 1: Default Behavior (No Prefs)
intent = Intent(ActionDomain.MEDIA, "play", {"query": "test song"}, "play test song")
advised = learning.advise(intent)
print(f"1. Default Platform Hint: {advised.hints.preferred_platform} (Expected: spotify)")

# Test 2: Set Preference
print("\nSetting preference: default_music_app = youtube")
learning.set_preference("default_music_app", "youtube")

intent2 = Intent(ActionDomain.MEDIA, "play", {"query": "another song"}, "play another song")
advised2 = learning.advise(intent2)
print(f"2. Advisory after pref change: {advised2.hints.preferred_platform} (Expected: youtube)")

# Test 3: Override
intent3 = Intent(ActionDomain.MEDIA, "play", {"query": "song", "platform": "apple music"}, "play song on apple music")
advised3 = learning.advise(intent3)
# Planner should respect explicit param over hint, but hint might still say youtube. 
# The Planner logic handles the precedence (Param > Hint). 
print(f"3. Hint remains: {advised3.hints.preferred_platform} (Expected: youtube)")
print(f"   Param remains: {advised3.parameters['platform']} (Expected: apple music)")

print("\n--- TEST COMPLETE ---")
