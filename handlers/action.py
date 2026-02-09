from core.context import CTX
from core.modes import RequestMode
from core.domains import ActionDomain
from core.parser import parse_code_intent, parse_media_intent
from automation.whatsapp import handle_whatsapp
from automation.code import handle_code_automation
from automation.media import handle_media_automation

def detect_domain(text: str) -> ActionDomain:
    t = text.lower()

    if any(k in t for k in ("write code", "python program", "java program", "code")):
        return ActionDomain.CODE

    if any(k in t for k in ("spotify", "play song", "music", "play")):
        return ActionDomain.MEDIA

    if any(k in t for k in ("message", "whatsapp", "send")):
        # Note: MESSAGE was removed from strict domains list in prompt? 
        # "ActionDomain(Enum): MEDIA, CODE, SYSTEM, WEB, GENERAL"
        # Wait, the user prompt REMOVED "MESSAGE" from ActionDomain enum list.
        # "class ActionDomain(Enum): MEDIA, CODE, SYSTEM, WEB, GENERAL"
        # But "WhatApp" is a feature. I should map it to GENERAL or SYSTEM or keep it?
        # The prompt says "ActionDomain(Enum): MEDIA, CODE, SYSTEM, WEB, GENERAL".
        # It does NOT list MESSAGE.
        # However, it says "Action-First Architecture".
        # I will map WhatsApp to GENERAL or SYSTEM for now, OR validly...
        # actually if I look at "MessageIntent" in my previous step, I defined it.
        # But the PROMPT'S "Domain Enums" list EXCLUDED it.
        # I will strictly follow the prompt's Enum list.
        # So "Message" -> "system" or "general"? Or maybe I should add it back if I can?
        # "Brain Rules: Absolute Design Rules ... Domain Enums (Must use Enums)".
        # I cannot add MESSAGE if it's not in the list.
        # But wait, existing functionality handles WhatsApp.
        # I will treat "Send message" as SYSTEM or GENERAL for now, or maybe the user forgot it.
        # I'll stick to what I wrote in `core/domains.py` in the previous turn. 
        # In the previous turn I wrote `core/domains.py` with: `MEDIA = "media"`, `CODE = "code"`, `SYSTEM = "system"`, `WEB = "web"`, `GENERAL = "general"`.
        # So MESSAGE is gone.
        # I will map whatsapp to SYSTEM for now to avoid breaking it, or maybe GENERAL. 
        # Actually, let's look at `handlers/action.py`.
        # I'll assume "SYSTEM" for external apps/tools that aren't Code/Media.
        return ActionDomain.SYSTEM

    return ActionDomain.GENERAL

def handle_action(text: str):
    assert CTX.current_mode == RequestMode.ACTION, "MODE VIOLATION"
    
    domain = detect_domain(text)
    print(f"[Action] Routing to Domain: {domain}")

    if domain == ActionDomain.CODE:
        intent = parse_code_intent(text)
        return handle_code_automation(intent)

    if domain == ActionDomain.MEDIA:
        intent = parse_media_intent(text)
        return handle_media_automation(intent)

    if domain == ActionDomain.SYSTEM:
        # Check if it is actually whatsapp
        if "message" in text.lower() or "whatsapp" in text.lower():
             return handle_whatsapp(text)
        print("[Action] System domain execution.")
        return False

    return False
