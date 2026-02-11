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

ALLOWABLE DOMAINS:
- MEDIA: Spotify, YouTube, Music, Video playing.
- CODE: Programming, Writing code, VS Code, Terminal.
- ACTION: App automation, System control, File operations, WhatsApp, Email.
- SEARCH: Web search, Read-only information gathering.
- CONTENT: Explanation, Answering questions, Writing text.
- SYSTEM: Self diagnostics, Error reporting.

OUTPUT FORMAT:
{
    "domain": "MEDIA" | "CODE" | "ACTION" | "SEARCH" | "CONTENT" | "SYSTEM",
    "action": "<specific_action_name>",
    "parameters": {
        "<param_name>": "<param_value>"
    },
    "confidence": <float_0_to_1>
}

DOMAIN SPECIFIC RULES:

1. MEDIA DOMAIN:
   - Action MUST be one of: 'play', 'pause', 'next', 'previous', 'stop', 'resume'.
   - Parameters MUST include 'query' (the song/video name) if action is 'play'.
   - Parameters SHOULD include 'platform_hint' if the user mentions a platform (e.g., "on Spotify", "on YouTube", "locally").
   - Normalize 'platform_hint' to: 'spotify', 'youtube', 'local', or null.
   - User saying "play my last song" -> action: "play", parameters: {"special": "last_song"}.

2. CODE DOMAIN:
   - Action: 'write_code', 'execute_command'.
   - Parameters: 'language', 'task'.

3. GENERAL:
   - If intent is ambiguous, set confidence < 0.5.
   - Do not hallucinate parameters.

EXAMPLES:
Input: "Play Blinding Lights on Spotify"
Output: {"domain": "MEDIA", "action": "play", "parameters": {"query": "blinding lights", "platform_hint": "spotify"}}

Input: "Resume music"
Output: {"domain": "MEDIA", "action": "resume", "parameters": {}}

Input: "Play something by Weeknd"
Output: {"domain": "MEDIA", "action": "play", "parameters": {"query": "something by weeknd", "platform_hint": null}}

Input: "Play my last song"
Output: {"domain": "MEDIA", "action": "play", "parameters": {"special": "last_song"}}
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
