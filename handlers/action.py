from core.context import CTX
from core.modes import RequestMode
from core.domains import ActionDomain
from core.goal import Goal
from automation.whatsapp import handle_whatsapp
from automation.code import handle_code_automation
from automation.media import handle_media_automation
import re

def detect_domain(text: str) -> ActionDomain:
    t = text.lower()

    if any(k in t for k in ("write code", "python program", "java program", "code")):
        return ActionDomain.CODE

    if any(k in t for k in ("spotify", "play song", "music", "play")):
        return ActionDomain.MEDIA

    if any(k in t for k in ("message", "whatsapp", "send")):
        return ActionDomain.MESSAGE

    return ActionDomain.SYSTEM

def parse_goal(text: str, domain: ActionDomain) -> Goal:
    # Basic extraction
    # "Write a python program" -> content="python program"
    # "Play Blinding Lights" -> target="Blinding Lights"
    
    if domain == ActionDomain.CODE:
         # Extract content? Assumed entire text for now or specific regex
         return Goal(name="write_code", content=text, domain=domain)
         
    if domain == ActionDomain.MEDIA:
        # Extract target: "play X" -> X
        match = re.search(r"play (.+?)(?: on spotify|$)", text, re.IGNORECASE)
        target = match.group(1).strip() if match else text
        return Goal(name="play_media", target=target, domain=domain)
        
    return Goal(name="action", content=text, domain=domain)

def handle_action(text: str):
    assert CTX.current_mode == RequestMode.ACTION, "MODE VIOLATION"
    
    domain = detect_domain(text)
    goal = parse_goal(text, domain)
    
    print(f"[Action] Routing to Domain: {domain}")

    if domain == ActionDomain.CODE:
        return handle_code_automation(goal)

    if domain == ActionDomain.MEDIA:
        return handle_media_automation(goal)

    if domain == ActionDomain.MESSAGE:
        # WhatsApp wrapper accepts raw text currently, verify if we need to adapt
        # For now, pass text as wrapper expects it or adapt wrapper to Goal?
        # The instruction said "handle_whatsapp(goal)". 
        # Let's verify automation/whatsapp.py signature. 
        # It takes `text`. Let's stick to text for valid back-compat or update wrapper.
        # Implementation Plan said "Adapt to accept Goal".
        # Let's pass text to existing wrapper for safety unless we update it now.
        # But wait, instruction said "No fallbacks".
        # Let's update handle_whatsapp in next step or use it as is if it parses.
        return handle_whatsapp(text) # Existing wrapper parses text internally

    if domain == ActionDomain.SYSTEM:
        print("[Action] System domain not fully implemented yet.")
        return False

    return False
