import asyncio
from Backend.Automation import Automation

async def test_complex_flow():
    print("Testing complex automation flow...")
    
    # 1. Open Notepad
    # 2. Type some text
    # 3. Press Enter
    # 4. Type more text
    
    commands = [
        "open chrome",
        "type python programming",
        "press enter"
    ]
    
    await Automation(commands)

if __name__ == "__main__":
    asyncio.run(test_complex_flow())
