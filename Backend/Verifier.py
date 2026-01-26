from rich import print

from Backend.ExpectationModel import ExpectationModel

class Verifier:
    def __init__(self):
        self.destructive_keywords = ["delete", "remove", "format", "shutdown", "kill"]
        self.expectation_model = ExpectationModel()

    def verify_plan(self, plan, risk_modifier=0.0, context=None, user_query=""):
        """
        Validates the plan. Returns (is_safe, risk_score, plan/reason).
        Risk Score: 0.0 (Safe) to 1.0 (Critical).
        """
        if not plan:
            return False, 0.0, "Empty plan"

        verified_plan = []
        max_risk = 0.0
        
        # Unwrap plan if it's the v3 dictionary format
        current_plan = plan.get("plan") if isinstance(plan, dict) else plan

        for step in current_plan:
            action = step.get("action")
            target = str(step.get("target", "")).lower()

            # Safety Rule 1: Destructive Actions
            if any(word in target for word in self.destructive_keywords):
                step["risk"] = "high"
                step["risk_score"] = 0.9
                step["requires_confirmation"] = True
                max_risk = max(max_risk, 0.9)
            elif action == "delete" or action == "remove":
                step["risk"] = "high"
                step["risk_score"] = 0.8
                step["requires_confirmation"] = True
                max_risk = max(max_risk, 0.8)
            else:
                step["risk"] = "safe"
                step["risk_score"] = 0.1
                step["requires_confirmation"] = False
                max_risk = max(max_risk, 0.1)

            verified_plan.append(step)

        # If v3 dict, re-wrap it
        if isinstance(plan, dict):
            plan["plan"] = verified_plan
        else:
            plan = verified_plan

        # Apply external risk modifier
        final_risk = min(1.0, max_risk + risk_modifier)
        
        # v4.0 Belief Mismatch & Context Adaptation
        if user_query:
            # 1. Infer Expectation
            expectation = self.expectation_model.infer_expectation(user_query, context)
            
            # 2. Detect Mismatch
            mismatch_score, reasons = self.expectation_model.detect_belief_mismatch(plan, expectation)
            
            if mismatch_score > 0.3:
                print(f"[Verifier] Belief Mismatch Detected (Score: {mismatch_score:.2f})")
                for r in reasons: print(f"  - {r}")
                
                final_risk += mismatch_score
                
            # 3. Contextual Confirmation Threshold
            if context:
                # If mismatch score exceeds surprise tolerance, FORCE block
                if mismatch_score > context.get("surprise_tolerance", 0.5):
                    print(f"[Verifier] Mismatch ({mismatch_score:.2f}) > Surprise Tolerance ({context.get('surprise_tolerance'):.2f}). BLOCKING.")
                    return False, 1.0, f"Action mismatch (Risk: {mismatch_score:.2f}) - Context requires confirmation."
                
                # If context demands high confirmation (low trust)
                if context.get("confirmation_threshold", 0.5) > 0.7:
                     final_risk += 0.2
                     print("[Verifier] Increased risk due to Context Confirmation Threshold.")

        if final_risk >= 0.7:
             # Logic for confirmation would handle this, returning safe=True but flag set
             # But if we want to force explicit PAUSE in GoalManager, we pass high risk.
             return True, final_risk, plan
        
        return True, final_risk, plan
