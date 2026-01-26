
import sys
import os

# Add the project root to sys.path so we can import Backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

try:
    from Backend.SpeechToText import SpeechRecognition
    print("Starting SpeechRecognition test...")
    print("Please say something within the next 5-10 seconds...")
    text = SpeechRecognition()
    print(f"Test Result: '{text}'")
except Exception as e:
    print(f"Test Failed with error: {e}")
