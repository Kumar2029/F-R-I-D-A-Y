from FRIDAY.core.models import Intent, ExecutionPlan, AutomationAction, VerificationResult
from Backend.MediaController import MediaController

class MediaPlanner:
    def __init__(self):
        self.controller = MediaController()

    def plan(self, intent: Intent) -> ExecutionPlan:
        # GMC handles everything (Intent Normalization, Platform, Verification)
        # We bridge FRIDAY Intent -> MediaIntent
        
        # 1. Normalize
        # FRIDAY Intent structure: action="play", parameters={"query": "...", "platform": "..."}
        # We reconstruct the raw query "play <query> on <platform>" for GMC normalization
        # OR better: usage internal normalization if we trust FRIDAY's slots.
        # But GMC normalization is "Layer 1" and robust. 
        # Let's perform a direct mapping.
        
        query = intent.parameters.get("query", "")
        platform = intent.parameters.get("platform", "")
        
        # If platform is empty, check hints
        if not platform and intent.hints and intent.hints.preferred_platform:
            platform = intent.hints.preferred_platform
            
        # Construct MediaIntent directly
        from core.intents import MediaIntent
        media_intent = MediaIntent(
            action=intent.action,
            query=query,
            platform_hint=platform if platform else None
        )
        
        # EXECUTING HERE (Blocking Call)
        # GMC is designed to be an executor.
        print(f"[MediaPlanner] Delegating to GMC: {media_intent}")
        success = self.controller.execute(media_intent)
        
        # Return a plan that reflects the result.
        # Since execution happened, we return an empty plan (or dummy success) 
        # so AutomationEngine doesn't try to re-run steps.
        # We can use a "noop" step or just return success if allowed.
        
        if success:
             # Return a dummy verification step that always passes, 
             # because GMC already verified.
             return ExecutionPlan(
                 intent=intent, 
                 steps=[], 
                 verification_step=AutomationAction(type="verify_success_signal", params={})
             )
        else:
             # Return valid plan but indicate failure? 
             # Or raise exception?
             # If we return empty steps, AutomationEngine does nothing.
             # We should probably return a failed verification step.
             return ExecutionPlan(
                 intent=intent, 
                 steps=[],
                 verification_step=AutomationAction(type="verify_fail_signal", params={"reason": "GMC Execution Failed"})
             )

