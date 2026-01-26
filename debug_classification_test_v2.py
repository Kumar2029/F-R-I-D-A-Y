
from groq import Groq
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

def Classify(prompt):
    messages = [
        {"role": "system", "content": "You are a classifier. You must classify the user's input into one of two categories: 'general' or 'realtime'.\n\n- 'general': Conversational questions, pleasantries, jokes, general knowledge, OR questions about the current time, date, or day (because I have that context).\n- 'realtime': Requests to EXECUTE a specific action on the computer (open apps, play media, control volume) OR search the web.\n\nReply ONLY with 'general' or 'realtime'."},
        {"role": "user", "content": f"{prompt}"}
    ]
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=10,
        temperature=0
    )
    
    return completion.choices[0].message.content.strip()

test_cases = [
    "What is the time?",
    "Open Chrome",
    "Who is the president of the USA?",
    "Play Taylor Swift on YouTube",
    "How are you?",
    "Search for weather in New York",
    "Turn up the volume"
]

print("Testing Classification (Refined)...")
for case in test_cases:
    print(f"'{case}' -> {Classify(case)}")
