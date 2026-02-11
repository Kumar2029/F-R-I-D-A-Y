from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction
from FRIDAY.layers.handlers.code_handler import CodeHandler
from groq import Groq
from dotenv import dotenv_values
import os
import time
import re
import ast

# Load Env (Duplicate load - could be in core.config)
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)

class CodePlanner:
    def __init__(self):
        self.code_handler = CodeHandler()

    def plan(self, intent: Intent) -> ExecutionPlan:
        steps = []
        action = intent.action.lower()
        task = intent.parameters.get("task", "")
        language = intent.parameters.get("language", "python").lower()
        
        if action == "write_code" or action == "execute_command":
            code_content = self.generate_code(task, language)
            
            # Generate filename from task (snake_case)
            # Remove common prefixes like "write a program to", "create a function to"
            clean_task = task.lower()
            prefixes = ["write a program to ", "write code to ", "create a function to ", "print ", "calculate ", "generate "]
            for p in prefixes:
                if clean_task.startswith(p):
                    clean_task = clean_task[len(p):]
            
            safe_name = re.sub(r'[^a-z0-9]', '_', clean_task).strip('_')
            safe_name = re.sub(r'_+', '_', safe_name)
            
            # Limit length
            if len(safe_name) > 50:
                 safe_name = safe_name[:50]
                 
            filename = f"{safe_name}.py"
            
            filename = f"{safe_name}.py"
            
            # DELEGATION: Backend-Driven Flow
            steps = self.code_handler.generate_backend_steps(code_content, filename)
            
            # 6. Verification
            steps.append(AutomationAction(type="speak", params={"text": f"Code for {task} generated and executed."}))
            
            verification = self.code_handler.get_verification_step(filename)
            
            return ExecutionPlan(intent=intent, steps=steps, verification_step=verification)

        return ExecutionPlan(intent=intent, steps=[])

    def generate_code(self, task: str, language: str) -> str:
        # STRICT SYSTEM PROMPT FOR CODE GEN
        prompt = f"""
        You are a generic coding engine. Write a robust {language} program to: {task}.
        
        RULES:
        1. Output ONLY the raw code. No markdown formatting (no ```python blocks). 
        2. No explanation. Just the code.
        3. The code MUST BE COMPLETE and RUNNABLE.
        4. If the task implies a calculation (e.g. "Calculate Fibonacci"), the code MUST print the result to stdout so verification can see it.
        5. Do not use input() unless explicitly asked. Hardcode example values if needed to demonstrate the logic.
        """
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            code = completion.choices[0].message.content
            code = completion.choices[0].message.content
            
            # Delegate to robust utility
            from FRIDAY.core.utils import code_cleanup
            return code_cleanup.clean_generated_code(code)

        except Exception as e:
            print(f"[CodePlanner] Gen Error: {e}")
            return f"print('Error generating code for {task}: {e}')"
