import re
from Backend.contracts import Goal

class GoalExtractor:
    def __init__(self):
        # Regex patterns are now less central, logic is prioritized
        pass

    def extract_contact_name(self, text):
        # 1. "to [name]"
        match = re.search(r"to\s+(.+?)(\s+(saying|that|with)|$)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 2. "whatsapp [name]" (fallback if no message found by other patterns)
        # We must be careful not to capture message content as name.
        # This runs if specific patterns failed.
        match_direct = re.search(r"^(?:whatsapp|text|msg|message|tell)\s+(?!to\s)(.+?)$", text, re.IGNORECASE)
        if match_direct:
            return match_direct.group(1).strip()
            
        return None

    def extract_message_content(self, text):
        match = re.search(r"(saying|that)\s+(.+)$", text, re.IGNORECASE)
        if match:
            return match.group(2).strip()
            
        match_embedded = re.search(r"send\s+(?:a\s+)?(.+?)\s+message\s+to\s+(.+)$", text, re.IGNORECASE)
        if match_embedded:
            return match_embedded.group(1).strip()
            
        return None

    def _infer_message_content(self, contact_name):
        """
        Infers a default message based on the contact relationship.
        v4 Requirement: Eliminate over-clarification.
        """
        c = contact_name.lower().strip()
        if any(x in c for x in ["mum", "mom", "mother", "dad", "father", "parent"]):
            return "Hi"
        if any(x in c for x in ["bro", "brother", "sis", "sister", "friend", "bestie"]):
            return "Hey"
        if any(x in c for x in ["boss", "sir", "manager", "lead"]):
            return "Hello, I wanted to reach out regarding work."
        
        # Default fallback
        return "Hello"

    def extract_goal(self, user_input):
        """
        Convert raw user input into an abstract goal.
        Input is assumed to be normalized (lowercase, no punctuation).
        Logic:
        1. CONTENT MODE (Reasoning, logic, code, generation)
        2. ACTION MODE (Automation) - Strict parameter checks
        3. QUERY MODE (Missing info or unclear)
        """
        clean_input = user_input.strip()

        # 1. CONTENT MODE (Reasoning, logic, code, generation)
        # Keywords from requirement
        content_keywords = ["write", "explain", "generate", "code", "pattern", "algorithm", 
                          "example", "story", "definition", "create"]
        
        # Exception: "generate image" is ACTION (handled later)
        # Exception: "create image" is ACTION
        is_image_gen = "image" in clean_input and ("generate" in clean_input or "create" in clean_input or "make" in clean_input)
        
        if not is_image_gen:
             for keyword in content_keywords:
                 if keyword in clean_input:
                     return Goal(
                         name="generate_content",
                         response_mode="CONTENT",
                         content=clean_input
                     )

        # 2. ACTION MODE (Automation)
        
        # A. WhatsApp / Message
        if "send" in clean_input or "message" in clean_input or "whatsapp" in clean_input or "tell" in clean_input:
            contact = None
            message = None
            
            # Pattern: "tell [name] [message]"
            if "tell" in clean_input:
                 match = re.search(r"(?i)^tell\s+(.+?)\s+(.+)$", clean_input)
                 if match:
                     contact, message = match.group(1).strip(), match.group(2).strip()
            
            # Pattern: "whatsapp [name] [message]"
            elif "whatsapp" in clean_input and not "send" in clean_input:
                 match = re.search(r"(?i)^(whatsapp|text|msg|message)\s+(.+?)\s+(.+)$", clean_input)
                 if match:
                     contact, message = match.group(2).strip(), match.group(3).strip()
            
            # General "send message" patterns
            else:
                 contact = self.extract_contact_name(clean_input)
                 message = self.extract_message_content(clean_input)
                 
                 # Pattern: "send message to [contact]" (Check if explicitly missing content)
                 if not contact and not message:
                      match = re.search(r"^send\s+(?:a\s+)?message\s+to\s+(.+)$", clean_input, re.IGNORECASE)
                      if match:
                           contact = match.group(1).strip()
            
            # DECISION LOGIC
            if contact:
                # v4 Upgrade: Infer message if missing
                if not message:
                    message = self._infer_message_content(contact)
                    print(f"[GoalExtractor] Inferred default message '{message}' for '{contact}'")
                
                return Goal(
                    name="send_message",
                    target=contact,
                    content=message,
                    priority="normal",
                    response_mode="ACTION"
                )
                 
            elif message and not contact:
                 return Goal(
                     name="clarify",
                     response_mode="QUERY",
                     content="Who should I send that message to?"
                 )
                 
            elif message and not contact:
                 return Goal(
                     name="clarify",
                     response_mode="QUERY",
                     content="Who should I send that message to?"
                 )
            
            # Ambiguous message intent -> QUERY
            return Goal(
                 name="clarify",
                 response_mode="QUERY",
                 content="Who do you want to message and what should I say?"
             )

        # B. Image Generation
        if is_image_gen:
            match = re.search(r"(?i)(generate|create|make)\s+(?:me\s+)?(?:(?:an?|the)\s+)?image\s+of\s+(.+)", clean_input)
            if match:
                 return Goal(
                     name="generate_image", 
                     content=match.group(2).strip(),
                     response_mode="ACTION"
                 )
            else:
                 return Goal(
                     name="clarify",
                     response_mode="QUERY",
                     content="What kind of image should I generate?"
                 )

        # C. Search
        match = re.search(r"(?i)^(?:friday\s+)?(?:please\s+)?(search|find|lookup)\s+(?:for\s+)?(.+)$", clean_input)
        if match:
             return Goal(
                 name="search_web", 
                 target=match.group(2).strip(),
                 response_mode="ACTION"
             )

        # D. Open App
        # Only strict "open [app]"
        match = re.search(r"(?i)^open\s+(.+)$", clean_input)
        if match:
            return Goal(
                name="open_application", 
                target=match.group(1).strip(),
                response_mode="ACTION"
            )
            
        # E. Play
        match = re.search(r"(?i)^play\s+(.+)$", clean_input)
        if match:
            return Goal(
                name="play_media",
                target=match.group(1).strip(),
                response_mode="ACTION"
            )

        # 3. QUERY MODE (Default Fallback)
        # Replaces "unsupported"
        return Goal(
            name="clarify",
            response_mode="QUERY",
            content="I am not sure how to help with that. Could you clarify?"
        )

if __name__ == "__main__":
    extractor = GoalExtractor()
    print(extractor.extract_goal("tell alex ill be late"))
    print(extractor.extract_goal("whatsapp dad hello"))
    print(extractor.extract_goal("write a python script"))
    print(extractor.extract_goal("send message to mum")) # Should be QUERY
