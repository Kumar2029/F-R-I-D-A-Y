import re

class Goal:
    def __init__(self, goal_id, target=None, content=None, priority="normal", constraints=None):
        self.goal_id = goal_id
        self.target = target
        self.content = content
        self.priority = priority
        self.constraints = constraints or {}

    def __repr__(self):
        return f"Goal(id={self.goal_id}, target={self.target}, content={self.content}, priority={self.priority})"


class GoalExtractor:
    def __init__(self):
        # Regex patterns for common goals
        self.patterns = [
            (r"(?i)(send|message|text|whatsapp|tell) (.+?) (that|saying) (.+)", "send_message"), # "Send Mom that I'm late"
            (r"(?i)(send|message|text|whatsapp|tell) (.+?) (.+)", "send_message"), # "WhatsApp Mom I'm late" (fallback)
            (r"(?i)(send a message to) (.+)", "send_message_incomplete"), # "Send a message to Mom"
            (r"(?i)(generate|create|make)\s+(?:me\s+)?(?:(?:an?|the)\s+)?image\s+of\s+(.+)", "generate_image"), # "Generate me an image of a flower"
        ]

    def normalize_entity(self, text: str) -> str:
        """
        Removes trailing punctuation and normalizes whitespace.
        Example: "brother 2." -> "brother 2"
        """
        if not text:
            return text

        # Remove leading/trailing whitespace
        text = text.strip()

        # Remove trailing punctuation (.,!?)
        text = re.sub(r"[.,!?]+$", "", text)

        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text)

        return text

    def extract_contact_name(self, text):
        # Heuristic: "to [Name]"
        match = re.search(r"to\s+(.+?)(\s+(saying|that|with)|$)", text, re.IGNORECASE)
        if match:
            return self.normalize_entity(match.group(1))
        return None

    def extract_message_content(self, text):
        # Heuristic: "saying [Message]" or "that [Message]" or just matches after contact
        # If explicit format "send a message to X saying Y"
        match = re.search(r"(saying|that)\s+(.+)$", text, re.IGNORECASE)
        if match:
            return self.normalize_entity(match.group(2))
        # Fallback: check if we split by "to [Name]"
        # If text is "Send a hi message to brother 2" -> This is tricky without strict pattern.
        # User example: "Send a hi message to brother 2" -> Content="hi", Contact="brother 2"
        # "Send a [Content] message to [Contact]"
        match_embedded = re.search(r"send\s+(?:a\s+)?(.+?)\s+message\s+to\s+(.+)$", text, re.IGNORECASE)
        if match_embedded:
            return self.normalize_entity(match_embedded.group(1))
            
        return None

    def extract_goal(self, user_input):
        """
        Convert raw user input into an abstract goal.
        """
        # cleans input
        clean_input = user_input.strip()

        # PART 1: EXPLICIT MESSAGING RULE (High Priority)
        # "Send a hi message to brother 2"
        if "send" in clean_input.lower() and "message" in clean_input.lower():
            # Sub-rule: "Send a message to [Contact]" (No content embedded)
            # This prevents capture of 'a' as content in the next rule.
            simple_match = re.search(r"^send\s+(?:a\s+)?message\s+to\s+(.+)$", clean_input, re.IGNORECASE)
            if simple_match:
                 return Goal(
                    goal_id="send_message",
                    target=self.normalize_entity(simple_match.group(1)),
                    content=None, # Content missing
                    priority="normal"
                )

            # Try embedded first: "Send a [Content] message to [Contact]"
            # This covers the user example perfectly.
            embedded_match = re.search(r"send\s+(?:a\s+)?(.+?)\s+message\s+to\s+(.+)$", clean_input, re.IGNORECASE)
            if embedded_match:
                return Goal(
                    goal_id="send_message",
                    target=self.normalize_entity(embedded_match.group(2)),
                    content=self.normalize_entity(embedded_match.group(1)),
                    priority="normal"
                )

            contact = self.extract_contact_name(clean_input)
            message = self.extract_message_content(clean_input)
            
            # Safety: Both must be present (Part 4)
            if contact and message:
                return Goal(
                    goal_id="send_message",
                    target=contact,
                    content=message,
                    priority="normal"
                )
             # If missing, fall through to other patterns or general chat

        # 1. Check for "Send Message" patterns
        # More robust regex for "Message [Person] [Content]"
        # Try specific patterns first
        
        # Pattern: "Tell [Name] [Message]"
        match = re.search(r"(?i)^tell\s+(.+?)\s+(.+)$", clean_input)
        if match:
             return Goal(
                 goal_id="send_message", 
                 target=self.normalize_entity(match.group(1)), 
                 content=self.normalize_entity(match.group(2))
             )

        # Pattern: "Send a message to [Name] saying [Message]"
        match = re.search(r"(?i)send\s+(?:a)?\s*message\s+to\s+(.+?)\s+(?:saying|that)\s+(.+)$", clean_input)
        if match:
            return Goal(
                goal_id="send_message", 
                target=self.normalize_entity(match.group(1)), 
                content=self.normalize_entity(match.group(2))
            )

        # Pattern: "WhatsApp [Name] [Message]" (We map 'WhatsApp' to generic send_message goal, NOT tool)
        match = re.search(r"(?i)^(whatsapp|text|msg|message)\s+(.+?)\s+(.+)$", clean_input)
        if match:
             return Goal(
                 goal_id="send_message", 
                 target=self.normalize_entity(match.group(2)), 
                 content=self.normalize_entity(match.group(3))
             )
        
        # Pattern: "Generate image of [Prompt]"
        match = re.search(r"(?i)(generate|create|make)\s+(?:me\s+)?(?:(?:an?|the)\s+)?image\s+of\s+(.+)", clean_input)
        if match:
             return Goal(goal_id="generate_image", content=self.normalize_entity(match.group(2)))
        
        # General Fallback for "Send message to X" without content (might be handled by Planner asking for content, or we assume content is missing)
        # For now, let's map unknown simple intents or rely on LLM if we had it here, but stick to rules.
        
        # Search Rule
        match = re.search(r"(?i)^(?:friday\s+)?(?:please\s+)?(search|find|lookup)\s+(?:for\s+)?(.+)$", clean_input)
        if match:
             return Goal(goal_id="search_web", target=self.normalize_entity(match.group(2)))

        # If no regex matches, maybe it's a "general" chat or "open" command?
        # The prompt says: "Convert raw user input into an abstract goal, independent of tools."
        # "Open Chrome" -> goal_id="open_application" (Abstract)
        match = re.search(r"(?i)^open\s+(.+)$", clean_input)
        if match:
            return Goal(goal_id="open_application", target=self.normalize_entity(match.group(1)))
            
        # Default/Unknown -> treated as general interaction or forwarded
        return Goal(goal_id="unknown_intent", content=clean_input)

if __name__ == "__main__":
    extractor = GoalExtractor()
    print(extractor.extract_goal("Tell Alex I'll be late"))
    print(extractor.extract_goal("WhatsApp Dad Hello"))
    print(extractor.extract_goal("Open Chrome"))
