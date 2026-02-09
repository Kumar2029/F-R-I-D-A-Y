from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction
from groq import Groq
from dotenv import dotenv_values
import os

# Load Env
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)

class GeneralPlanner:
    def plan(self, intent: Intent) -> ExecutionPlan:
        # For general questions, the "Action" is to "Speak the Answer".
        # We can generate the answer here using LLM, then create an automation step to speak it.
        
        query = intent.parameters.get("query") or intent.original_query
        
        answer = self.generate_answer(query)
        
        steps = [
            AutomationAction(type="speak", params={"text": answer})
        ]
        
        return ExecutionPlan(intent=intent, steps=steps)

    def generate_answer(self, query: str) -> str:
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Answer briefly and concisely in 1-2 sentences."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[GeneralPlanner] LLM Error: {e}")
            return "I'm having trouble thinking right now."
