from Backend.contracts import Goal, Strategy
from Backend.outcomes import Outcome

class OutcomeVerifier:
    def verify(self, goal: Goal, strategy: Strategy, outcome: Outcome) -> bool:
        """
        Decides whether the outcome is acceptable.
        
        Returns:
            True: Outcome is acceptable (success).
            False: Outcome is unacceptable (failure), requires retry or fallback.
        """
        if outcome.success:
            return True

        # If we are here, it failed.
        # Simple verifier: Failure is failure.
        # Advanced logic (future): Check if "partial success" is acceptable?
        # For Stage 2, strict success is required.
        return False

    def can_retry(self, outcome: Outcome, attempts: int, max_attempts: int) -> bool:
        """
        Decides if a retry is worthwhile based on the failure reason.
        
        Args:
            outcome: The failed outcome.
            attempts: Current attempt count (already executed).
            max_attempts: Total allowed attempts.
            
        Returns:
            True if we should retry, False if we should escalate/fail.
        """
        if attempts >= max_attempts:
            return False

        reason = (outcome.reason or "").lower()

        # RETRYABLE ERRORS (Transient)
        retryable_keywords = [
            "focus", "timeout", "not found", "window", "loading", "ready", 
            "clip", "unavailable", "busy", "locked", "network", "lag"
        ]
        
        if any(k in reason for k in retryable_keywords):
            return True

        # NON-RETRYABLE ERRORS (Logic/Permanent)
        # e.g. "Unknown command", "Unsupported", "Auth failed"
        # If reason is NOT in retryable, do we retry? 
        # Better to be conservative: Retry only known transient issues.
        # But for robustness, maybe one generic retry is okay?
        # User Prompt Rule: "Retry ONLY if failure is focus/timing/window... NEVER retry logic errors".
        
        return False
