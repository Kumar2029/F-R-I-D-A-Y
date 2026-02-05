
from rich import print

class ExpectationModel:
    def __init__(self):
        # Keywords that imply specific scopes
        self.scope_keywords = {
            "low": ["open", "launch", "start", "show", "close", "stop"],
            "medium": ["search", "find", "google", "lookup", "check"],
            "high": ["send", "write", "message", "email", "play", "create", "make", "generate"]
        }
        
        # High Risk / Irreversible Actions that tend to cause mismatch if not explicitly requested
        self.irreversible_actions = ["send", "delete", "remove", "buy", "post", "tweet", "publish"]

    def infer_expectation(self, user_query: str, context: dict = None):
        """
        Infers the user's likely expectation profile.
        Returns v4 format:
        {
            "expected_scope": "low" | "medium" | "high",
            "expected_autonomy": "low" | "high", 
            "expected_actions": [...],
            "confidence": 0.0-1.0
        }
        """
        query = user_query.lower().strip()
        
        # 1. Determine Scope Trigger
        scope = "high" # Default to high/complex
        confidence = 0.5
        
        # Check Low Scope (strong override)
        for word in self.scope_keywords["low"]:
            if query.startswith(f"{word} ") or query == word:
                scope = "low"
                confidence = 0.9
                break
        
        # Check Medium Scope
        if scope != "low":
            for word in self.scope_keywords["medium"]:
                if query.startswith(f"{word} ") or query == word:
                    scope = "medium"
                    confidence = 0.8
                    break

        # 2. Determine Action Whitelist based on Scope
        expected_actions = []
        if scope == "low":
            expected_actions = ["open", "close", "wait", "system", "speak"]
        elif scope == "medium":
            expected_actions = ["open", "close", "wait", "type", "press", "search_web", "google search", "youtube search", "system", "speak"]
        else: # High
            expected_actions = ["open", "close", "wait", "type", "press", "search_web", "google search", "youtube search", "play", "content", "system", "send", "click", "send_whatsapp", "generate_image", "speak"]

        # 3. Determine Autonomy based on Context (Trust/Patience)
        # In v4, we use the ContextEngine output passed as 'context'
        expected_autonomy = "high"
        if context:
            # If system autonomy is low or surprise tolerance is low, user expects LOW autonomy
            if context.get("autonomy_level", 0.5) < 0.4:
                expected_autonomy = "low"
                confidence += 0.1 # We are strictly adhering to low autonomy

        profile = {
            "expected_scope": scope,
            "expected_autonomy": expected_autonomy,
            "expected_actions": expected_actions,
            "confidence": min(1.0, confidence)
        }
        
        return profile

    def detect_belief_mismatch(self, plan: list, expectation: dict):
        """
        Calculates a mismatch score (0.0 to 1.0).
        0.0 = Aligned
        1.0 = Severe Mismatch (Pause immediately)
        """
        score = 0.0
        reasons = []
        
        expected_actions = expectation.get("expected_actions", [])
        expected_scope = expectation.get("expected_scope", "high")
        
        # Unwrap plan if needed
        steps = plan.get("plan", []) if isinstance(plan, dict) else plan
        
        for step in steps:
            action = step.get("action", "").lower()
            target = str(step.get("target", "")).lower()
            
            # Rule 1: Action not in whitelist (Severity: MEDIUM-HIGH)
            if action not in expected_actions:
                score += 0.5
                reasons.append(f"Action '{action}' outside expected scope '{expected_scope}'")
            
            # Rule 2: Irreversible Action detected (Severity: HIGH)
            # If the user didn't explicitly ask for it (which we assume implies high scope/whitelist inclusion)
            # But even if 'send' is in 'expected_actions' for High Scope, we might want to check 
            # if the query was VAGUE. 
            # For now, simplistic check:
            if action in self.irreversible_actions:
                # If we are doing something irreversible, we double check context
                # Just add specific risk
                score += 0.2
                reasons.append(f"Irreversible action '{action}' increases mismatch risk")

        # Rule 3: Autonomy Mismatch
        # If user expects LOW autonomy (e.g. "Wait for me"), but plan has many steps
        if expectation["expected_autonomy"] == "low" and len(steps) > 1:
            score += 0.3
            reasons.append(f"Goal has {len(steps)} steps but user expects Low Autonomy")

        final_score = min(1.0, score)
        return final_score, reasons

if __name__ == "__main__":
    em = ExpectationModel()
    
    # Test 1: Low Scope Mismatch
    print("\n--- TEST: 'Open WhatsApp' vs [Send Message] ---")
    exp = em.infer_expectation("Open WhatsApp")
    plan = [{"action": "open", "target": "whatsapp"}, {"action": "send", "target": "msg"}]
    score, reasons = em.detect_belief_mismatch(plan, exp)
    print(f"Expectation: {exp['expected_scope']}")
    print(f"Plan Actions: {[s['action'] for s in plan]}")
    print(f"Mismatch Score: {score}")
    print(f"Reasons: {reasons}")
    
    # Test 2: Aligned
    print("\n--- TEST: 'Open WhatsApp' vs [Open] ---")
    plan_aligned = [{"action": "open", "target": "whatsapp"}]
    score, reasons = em.detect_belief_mismatch(plan_aligned, exp)
    print(f"Mismatch Score: {score}")
