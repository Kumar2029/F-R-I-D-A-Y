import re
from Backend.Automation import secure_send_whatsapp

def extract_contact_and_message(text):
    # Determine contact and message from text
    # Heuristic: "message to [CONTACT] [content]" or "message to [CONTACT] saying [content]"
    # or just "message [CONTACT] [content]"
    
    # Simple regex for "message to X saying Y"
    match = re.search(r"message to (.+?) saying (.+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    # Regex for "message to X" (assume prompt for content or just open chat)
    match = re.search(r"message to (.+)", text, re.IGNORECASE)
    if match:
        contact = match.group(1).strip()
        # If content not specified, maybe we should ask? For now, empty message or error.
        # "send a message to Vasanth" -> executed as opening chat? 
        # secure_send_whatsapp requires message.
        # If message is missing, we might default to " " to just open chat, or fail.
        # Let's assume the user provided content or we parse heavily.
        
        # Try to find content after contact
        # If text ends with contact, we have no content.
        return contact, " " # Open chat with empty draft? 

    return None, None

def handle_whatsapp(text: str):
    print(f"[Action] Handling WhatsApp: {text}")
    
    # improved extraction logic (porting from old GoalManager/GSO concepts implicitly)
    # The user said "Do not simplify logic" but also "No LLM".
    # Relying on regex for now as a strict rule.
    
    # "send a message to vasanth" -> contact="vasanth", content=" " (or ask?)
    # "send a message to vasanth saying hello" -> contact="vasanth", content="hello"
    
    contact, message = extract_contact_and_message(text)
    
    if not contact:
        print("[Action] Could not extract contact.")
        return False
        
    if not message:
        message = " " # default
    
    # Call the robust backend
    return secure_send_whatsapp(contact, message)
