from Backend.GoalManager import GoalManager
from rich import print
from groq import Groq
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)
goal_manager = GoalManager()

def Classify(prompt):
    messages = [
        {"role": "system", "content": "You are a classifier. You must classify the user's input into one of two categories: 'general' or 'realtime'.\n\n- 'general': Conversational questions, pleasantries, jokes, general knowledge, OR questions about the current time, date, or day (because I have that context).\n- 'realtime': Requests to EXECUTE a specific action on the computer (open apps, play media, control volume) OR search the web.\n\nReply ONLY with 'general' or 'realtime'."},
        {"role": "user", "content": f"{prompt}"}
    ]
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=10,
            temperature=0
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Classification Error: {e}")
        return "general" # Default to chat if classifier fails

# Supervisor Logic (v3 Adapter)
def FirstLayerDMM(prompt: str = "test"):
    print(f"\n[Supervisor v3] Received request: {prompt}")
    
    # 1. Classify Intent
    intent = Classify(prompt)
    print(f"[Supervisor v3] Intent Detected: {intent}")
    
    # 2. Automation Logic
    if "realtime" in intent.lower():
        # Execute Goal
        goal_id = goal_manager.create_goal(prompt)
        result_message = goal_manager.execute_goal(goal_id)
        
        # Check for failure/recommendation language
        if "Failed" in result_message or "Recommendation" in result_message:
             return [f"alert {result_message}"]
        
        return [f"general {result_message}"]

    # 3. General Chat Logic
    else:
        # Pass directly to Chatbot (Main.py handles 'general' tag)
        return [f"general {prompt}"]

if __name__ == "__main__":
    print(FirstLayerDMM("open chrome"))
    print(FirstLayerDMM("how are you?"))