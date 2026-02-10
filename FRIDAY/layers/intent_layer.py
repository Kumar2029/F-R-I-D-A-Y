import json
import os
from dotenv import dotenv_values
from groq import Groq
from FRIDAY.core.models import Intent, ActionDomain

# Load Env
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)

SYSTEM_PROMPT = """
You are the Intent Parsing Layer for the FRIDAY AI Assistant.
Your job is to convert raw user text into a strict JSON Intent Object.

ALLOWED DOMAINS:
- MEDIA: Spotify, YouTube, Music, Video
- CODE: Programming, Writing code, VS Code, Terminal
- SYSTEM: App control, Volume, Brightness, Shutdown
- MEDIA: Spotify, YouTube, Playing media (Strictly verified)
- CODE: Writing code, Opening VS Code, Creating files, Running code (Strictly Verified)
- ACTION: App automation, System control, File operations, WhatsApp, Email, Send Message
- SEARCH: Web search, Read-only information gathering (NO execution)
- CONTENT: Explanation, Answering questions, Writing text ONLY (NO automation)
- SYSTEM: Self diagnostics, Error reporting (DO NOT USE for app control or messages)

OUTPUT FORMAT:
{
    "domain": "MEDIA" | "CODE" | "ACTION" | "SEARCH" | "CONTENT" | "SYSTEM",
    "action": "<specific_action_name>",
    "parameters": {
        "<param_name>": "<param_value>"
    },
    "confidence": <float_0_to_1>
}

RULES:
1. If parameters are missing, do not guess. Return what is present.
2. If intent is ambiguous, set confidence < 0.5.
3. For CODE, 'action' should be 'write_code' or 'execute_command'.
4. For MEDIA, 'action' should be 'play', 'pause', 'next'.
5. For SEARCH, 'action' should be 'search'.
6. For CONTENT, 'action' should be 'chat' or 'explain'.
7. For ACTION, 'action' should be 'open_app', 'send_message', 'click'.

EXAMPLES:
Input: "Play Blinding Lights on Spotify"
Output: {"domain": "MEDIA", "action": "play", "parameters": {"query": "Blinding Lights", "platform": "spotify"}}

Input: "Write a python script to calculate factorial"
Output: {"domain": "CODE", "action": "write_code", "parameters": {"language": "python", "task": "calculate factorial"}}

Input: "What is the capital of France?"
Output: {"domain": "CONTENT", "action": "explain", "parameters": {"query": "capital of France"}}

Input: "Search for falcons on google"
Output: {"domain": "SEARCH", "action": "search", "parameters": {"query": "falcons"}}

Input: "Open Calculator"
Output: {"domain": "ACTION", "action": "open_app", "parameters": {"app_name": "Calculator"}}

Input: "Send a message to John saying Hello"
Output: {"domain": "ACTION", "action": "send_message", "parameters": {"contact": "John", "message": "Hello"}}
"""

def parse_intent(text: str) -> Intent:
    """
    Converts raw text into a structured Intent object.
    """
    if not text:
        raise ValueError("Input text cannot be empty")

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        response_content = completion.choices[0].message.content
        data = json.loads(response_content)
        
        # Map string domain to Enum
        domain_str = data.get("domain", "").upper()
        try:
            domain_enum = ActionDomain[domain_str]
        except KeyError:
             # Fallback or error? Strict requirement says "If intent is ambiguous -> refuse"
             # We'll treat unknown domain as low confidence/error
             print(f"[IntentLayer] Unknown domain: {domain_str}")
             return Intent(ActionDomain.SYSTEM, "unknown", {}, text, 0.0)

        intent = Intent(
            domain=domain_enum,
            action=data.get("action", "unknown"),
            parameters=data.get("parameters", {}),
            original_query=text,
            confidence=data.get("confidence", 0.0)
        )
        
        return intent

    except Exception as e:
        print(f"[IntentLayer] Error parsing intent: {e}")
        # Return a safe failure intent
        return Intent(ActionDomain.SYSTEM, "error", {"error": str(e)}, text, 0.0)
