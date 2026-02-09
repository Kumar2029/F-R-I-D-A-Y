from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction
from groq import Groq
from dotenv import dotenv_values
import os

# Load Env (Duplicate load - could be in core.config)
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)

class CodePlanner:
    def plan(self, intent: Intent) -> ExecutionPlan:
        steps = []
        action = intent.action.lower()
        task = intent.parameters.get("task", "")
        language = intent.parameters.get("language", "python").lower()
        
        if action == "write_code" or action == "execute_command":
            code_content = self.generate_code(task, language)
            
            # Use timestamp to avoid overwrite collisions
            import time
            timestamp = int(time.time())
            filename = f"generated_code_{timestamp}.py"
            
            # 1. Open VS Code
            steps.append(AutomationAction(type="open_app", params={"app_name": "Visual Studio Code"}))
            steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))
            
            # 2. New File
            steps.append(AutomationAction(type="press_key", params={"key": "ctrl+n"}))
            steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
            
            # 3. Paste Code (Faster/Reliable than type)
            steps.append(AutomationAction(type="paste_text", params={"text": code_content}))
            steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
            
            # 4. Save File
            steps.append(AutomationAction(type="press_key", params={"key": "ctrl+s"}))
            steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
            steps.append(AutomationAction(type="type_text", params={"text": filename}))
            steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
            steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
            steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
            
            # 5. Run Code (Terminal)
            # Open Terminal
            steps.append(AutomationAction(type="press_key", params={"key": "ctrl+`"})) 
            steps.append(AutomationAction(type="wait", params={"seconds": 1.0}))
            # Run
            steps.append(AutomationAction(type="type_text", params={"text": f"python {filename}"}))
            steps.append(AutomationAction(type="wait", params={"seconds": 0.5}))
            steps.append(AutomationAction(type="press_key", params={"key": "enter"}))
            
            # 6. Verification
            steps.append(AutomationAction(type="wait", params={"seconds": 2.0}))
            steps.append(AutomationAction(type="speak", params={"text": f"Code for {task} written and executed."}))
            
            verification = AutomationAction(
                 type="verify_file_exists",
                 params={"path": filename} # This might fail if path is wrong.
            )
            
            return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)

        return ExecutionPlan(intent=intent, steps=[])

    def generate_code(self, task: str, language: str) -> str:
        prompt = f"""
        You are a coding engine. Write a {language} program to: {task}.
        Output ONLY the raw code. No markdown formatting (no ```python blocks). 
        No explanation. Just the code.
        """
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            code = completion.choices[0].message.content
            # Clean up if markdown was included despite instructions
            code = code.replace("```python", "").replace("```", "").strip()
            return code
        except Exception as e:
            print(f"[CodePlanner] Gen Error: {e}")
            return f"# Error generating code for {task}"
