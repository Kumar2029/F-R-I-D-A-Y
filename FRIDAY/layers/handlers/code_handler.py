import os
import time
from typing import List, Optional, Tuple
from FRIDAY.core.models import AutomationAction

class CodeHandler:
    """
    Deterministic VS Code Automation Handler.
    Implements strict 7-phase execution sequence for robust code writing.
    
    PHASES:
    1. Intent Extraction (external)
    2. Code Planning (external)
    3. Code Generation (external)
    4. VS Code Automation (Open, New, Paste, Save)
    5. Execution (Run in Terminal)
    6. Error Handling (Retry - TODO)
    7. Save Guarantee
    """

    def write_code_in_vscode(self, code_content: str, filename: str) -> List[AutomationAction]:
        """
        Generates automation steps to write, save, and execute code in VS Code.
        """
        steps = []
        
        # Enforce Absolute Path
        abs_path = os.path.join(os.getcwd(), filename)
        
        # PHASE 4: VS CODE AUTOMATION
        # 1. Open VS Code
        steps.append(AutomationAction(type="open_app", params={"app_name": "Visual Studio Code"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))
        
        # 2. New File
        steps.append(AutomationAction(type="press_key", params={"key": "ctrl+n"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
        
        # 3. Paste Code (Faster/Reliable than type)
        steps.append(AutomationAction(type="paste_text", params={"text": code_content}))
        steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
        
        # 4. Save File (Absolute Path)
        steps.append(AutomationAction(type="press_key", params={"key": "ctrl+s"}))
        steps.append(AutomationAction(type="wait", params={"seconds": 1.5}))
        
        # Use PASTE for path (Handles spaces/symbols better)
        steps.append(AutomationAction(type="paste_text", params={"text": abs_path}))
        steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
        steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
        
        # Handle "File exists" Overwrite Prompt (Alt+Y usually confirms 'Yes')
        steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
        steps.append(AutomationAction(type="press_key", params={"key": "alt+y"})) 
        
        steps.append(AutomationAction(type="wait", params={"seconds": 1.5}))
        
        # PHASE 5: EXECUTION
        # 5. Run Code (Terminal - Absolute Path)
        # Open Terminal
        steps.append(AutomationAction(type="press_key", params={"key": "ctrl+`"})) 
        steps.append(AutomationAction(type="wait", params={"seconds": 1.5}))
        
        # Clear previous (optional)
        # steps.append(AutomationAction(type="type_text", params={"text": "cls"}))
        # steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
        
        # Run
        steps.append(AutomationAction(type="type_text", params={"text": f"python \"{abs_path}\""}))
        steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
        steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
        
        # Wait for execution (Simple scripts)
        steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))

        return steps

    def get_verification_step(self, filename: str) -> AutomationAction:
        abs_path = os.path.join(os.getcwd(), filename)
        # Verify by RUNNING the code and checking exit code 0
        return AutomationAction(
             type="verify_command_execution",
             params={"command": f"python \"{abs_path}\""} 
        )
