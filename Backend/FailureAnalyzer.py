from Backend.MemoryManager import MemoryManager
import datetime

class FailureAnalyzer:
    def __init__(self):
        self.memory = MemoryManager()

    def analyze_failure(self, goal_type, context, failure_stage, failure_reason):
        """
        Analyzes a failure and returns a corrective action.
        """
        timestamp = datetime.datetime.now().isoformat()
        
        failure_record = {
            "goal_type": goal_type,
            "context": context,
            "failure_stage": failure_stage,
            "failure_reason": failure_reason,
            "timestamp": timestamp,
            "user_aborted": failure_reason == "user_abort"
        }
        
        self.memory.record_failure(failure_record)
        
        # STAGE 4: DIAGNOSTIC LOGIC
        reason_lower = failure_reason.lower()
        correction = "RETRY" # Default
        
        if "focus" in reason_lower or "active" in reason_lower:
            correction = "REFOCUS"
        elif "not found" in reason_lower or "missing" in reason_lower:
             # If element missing, maybe app isn't open or wrong page
             correction = "REOPEN" 
        elif "typing" in reason_lower or "input" in reason_lower:
             correction = "RETYPE"
        elif "network" in reason_lower or "timeout" in reason_lower:
             correction = "WAIT"
        elif "logic" in reason_lower or "unknown" in reason_lower:
             correction = "ABORT"

        # Escalation based on history
        past_failures = self.memory.get_failures_by_goal(goal_type)
        failure_count = len(past_failures)
        
        if failure_count >= 3:
            correction = "ABORT"
            
        print(f"[FailureAnalyzer] Diagnosis: {failure_reason} -> {correction}")

        return {
            "correction": correction,
            "risk_modifier": 0.2 * failure_count,
            "recommendation": correction, # Legacy compatibility
            "failure_count": failure_count
        }

    def get_learning_context(self, goal_type):
        """
        Returns a summary of past failures to guide the Planner.
        """
        failures = self.memory.get_failures_by_goal(goal_type)
        if not failures:
            return None
            
        return f"WARNING: This goal ('{goal_type}') has failed {len(failures)} times previously. Reasons: {', '.join([f['failure_reason'] for f in failures[-3:]])}."
