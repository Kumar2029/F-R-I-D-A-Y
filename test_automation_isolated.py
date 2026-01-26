import asyncio
from Backend.Automation import Automation

async def test():
    print("--- Starting Isolation Test ---")
    # Using a safe command like 'system volume up' or just verifying 'open notepad' logic logic (mocked or real)
    # The prompt asked for 'open notepad'. Automation logic for 'open' uses OpenApp.
    # Note: OpenApp might fail if notepad is not found or not in path, but logging should appear.
    
    # We'll use 'system mute' as it is less intrusive/safer to test logic than opening apps, 
    # BUT the specific instruction was 'open notepad'. 
    # I will stick to the user's requested test case: "open notepad"
    
    await Automation(["open notepad"])

if __name__ == "__main__":
    asyncio.run(test())
