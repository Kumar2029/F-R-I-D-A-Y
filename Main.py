from stt.listener import listen
from core.supervisor import supervise
from Frontend.GUI import GraphicalUserInterface, SetAsssistantStatus
import threading
import sys

# Ensure we are running from the correct directory context
sys.path.append('d:\\JARVIS 2\\jarvis-ai-assistant')

def AssistantLoop():
    print("JARVIS Refactored Main Loop Started (Strict Domain Routing)")
    
    # Optional: Warmup or Init checks?
    
    while True:
        try:
            print("\nListening...")
            SetAsssistantStatus("Listening...")
            text = listen()
            
            if not text:
                continue
                
            print(f"[Main] User said: {text}")
            SetAsssistantStatus("Thinking...")
            supervise(text)
            SetAsssistantStatus("Ready")
            
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"FATAL ERROR in Main Loop: {e}")
            # Continue loop to avoid crash, but log error
            pass

if __name__ == "__main__":
    # Start Assistant Logic in a separate thread so GUI doesn't freeze
    thread = threading.Thread(target=AssistantLoop, daemon=True)
    thread.start()
    
    # Run GUI in the main thread (Required by PyQt)
    GraphicalUserInterface()