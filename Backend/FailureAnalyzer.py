from Backend.MemoryManager import MemoryManager
import datetime

class FailureAnalyzer:
    def __init__(self):
        self.memory = MemoryManager()

    def analyze_failure(self, goal_type, context, failure_stage, failure_reason):
        """
        Analyzes a failure, records it, and returns an adaptation strategy.
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
        
        # LEARNING LOGIC
        past_failures = self.memory.get_failures_by_goal(goal_type)
        failure_count = len(past_failures)
        
        # Rule A: Confidence Decay
        # Each failure reduces confidence by 25%
        confidence_decay = 0.75 ** failure_count
        
        # Rule B: Risk Escalation
        # Each failure adds 0.2 to risk score
        risk_escalation = 0.2 * failure_count
        
        # Rule C: Forced Clarification / Mode Switch
        recommendation = "RETRY"
        if failure_count >= 2:
            recommendation = "ASK_USER"
        elif failure_count >= 1:
            recommendation = "CAUTIOUS_RETRY"
            
        return {
            "confidence_modifier": confidence_decay,
            "risk_modifier": risk_escalation,
            "recommendation": recommendation,
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
