from typing import List, Tuple
from FRIDAY.core.models import Intent, AutomationAction, VerificationResult, AutomationAction as Action
from FRIDAY.layers.executors.base_executor import BaseExecutor

class LocalExecutor(BaseExecutor):
    def create_play_plan(self, intent: Intent) -> Tuple[List[AutomationAction], AutomationAction]:
        query = intent.parameters.get("query", "")
        steps = []
        
        # 1. Search Logic would go here (Scanning dirs)
        # For now, we assume a designated music folder
        music_dir = "C:\\Users\\kumar\\Music" 
        
        # We delegate the "Finding" to a python script step? 
        # Or we do it here in the planner?
        # Planner should be fast. 
        # Ideally, we create a step `find_and_play_file` that the automation engine handles.
        # But our AutomationEngine is primitive.
        
        # Let's use a "run_terminal_command" to use VLC or default player with a glob?
        # Check if query is a filename
        
        # Simplified:
        steps.append(Action(type="speak", params={"text": f"Searching for {query} locally."}))
        
        # PowerShell command to find and open
        # Get-ChildItem -Path C:\Users\kumar\Music -Recurse -Filter "*query*" | Select-Object -First 1 | ForEach-Object { Invoke-Item $_.FullName }
        ps_command = f'powershell -c "Get-ChildItem -Path {music_dir} -Recurse -Filter *{query}* | Select-Object -First 1 | ForEach-Object {{ Invoke-Item $_.FullName }}"'
        
        steps.append(Action(type="run_terminal_command", params={"command": ps_command}))
        steps.append(Action(type="wait", params={"seconds": 2.0}))

        # Verification
        # Hard to verify generic local player without knowing process name.
        # We can try verify_audio_activity if available later.
        verification = Action(type="verify_success_signal", params={})
        
        return steps, verification
