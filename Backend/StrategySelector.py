import json
import os

class Strategy:
    def __init__(self, strategy_id, confidence, reason, fallbacks=None):
        self.strategy_id = strategy_id
        self.confidence = confidence
        self.reason = reason
        self.fallbacks = fallbacks or []
    
    def __repr__(self):
        return f"Strategy(id={self.strategy_id}, confidence={self.confidence}, reason={self.reason})"


from Backend.OutcomeManager import OutcomeManager

# Global or class-level OutcomeManager, but user provided global in snippet
outcome_manager = OutcomeManager()

def bias_strategy(strategy_id, goal_id, target):
    outcomes = outcome_manager.recent_outcomes(goal_id, target)

    if len(outcomes) < 2:
        return 1.0  # no bias

    failures = sum(1 for o in outcomes if not o["success"])

    if failures >= 2:
        return 0.5  # penalize strategy

    # Calculate average confidence; handle missing key if mixing old/new data
    # New outcome record has "confidence". Old might not.
    try:
        avg_conf = sum(o.get("confidence", 0.5) for o in outcomes) / len(outcomes)
    except:
        avg_conf = 0.5

    return round(min(1.2, max(0.6, avg_conf)), 2)

class StrategySelector:
    def __init__(self, outcome_manager=None):
        self.outcome_manager = outcome_manager # Optional integration for history

    def select_strategy(self, goal, user_state=None):
        """
        Choose how to fulfill a goal using system knowledge, memory, and user state.
        """
        if goal.goal_id == "send_message":
            return Strategy(
                strategy_id="send_whatsapp",
                confidence=0.9,
                reason="Messaging intent maps to WhatsApp automation"
            )
        
        if goal.goal_id == "open_application":
            return self._select_open_strategy(goal)
            
        if goal.goal_id == "search_web":
             return Strategy(
                 strategy_id="search_web",
                 confidence=0.95,
                 reason="Web search intent maps to search_web tool"
             )

        if goal.goal_id == "generate_image":
            # PART 3: ADD STRATEGY: generate_image_local
            # Prefer Local SD (Offline, Free, Reliable)
            
            # Check if we should fallback to HF (e.g. if local is known broken? 
            # User says "HF may remain as quarantined fallback only". 
            # But the primary return should be local.
            
            return Strategy(
                strategy_id="generate_image_local",
                confidence=0.95,
                reason="Local Stable Diffusion (offline, reliable, free)"
            )
            
            # Legacy/Quarantined HF logic removed from primary path. 
            # It will only be reached if this strategy fails via fallback mechanisms if implemented?
            # Actually GSO Planner takes one strategy. 
            # If I return this, the system uses this.
            # If it fails, "GSO execution failed -> Fallback to Legacy".
            # The prompt says "HF may remain as quarantined fallback only". 
            # My 'Strategy' object supports 'fallbacks' list.
            # I can add HF there? 
            # But the user logic says "return Strategy(...)".
            # I will follow "IMPLEMENT EXACTLY":
            # return Strategy(..., strategy_id="generate_image_local", ...)
            
            # Original HF check removed/bypassed as per instruction "Remove Hugging Face as primary".
            
        # Default Strategy -> REMOVED (Strict Contract)
        # If no specific strategy maps to the goal, we cannot execute blindly.
        return None

    def _select_message_strategy(self, goal):
        contact = goal.target
        
        # Check history if available
        whatsapp_confidence = 0.8 # Base confidence (Subjective start)
        sms_confidence = 0.5
        
        if self.outcome_manager:
            # Check success rate for 'whatsapp' strategy
            stats = self.outcome_manager.get_strategy_stats("send_whatsapp")
            if stats["count"] > 0:
                print(f"[StrategySelector] WhatsApp Stats: {stats}")
                if stats["success_rate"] < 0.4:
                     whatsapp_confidence = 0.3 # Penalize heavily if frequently failing
                     print("[StrategySelector] Downgrading WhatsApp confidence due to poor history.")
                elif stats["success_rate"] > 0.8:
                     whatsapp_confidence = 0.95 # Boost if reliable
            
            # Check for recent failures (Consecutive)
            # Need a method in OutcomeManager for this? calculate_confidence uses retries.
            # Simple check: last outcome for this goal/strategy
            pass

        # Rule-based Preference
        # If we have history or specific contact info, we'd check it.
        # For now, default to WhatsApp as primary if high confidence, else SMS.
        
        # Example Logic: "Prefer WhatsApp if contact exists and success rate > 0.7"
        # Since we don't have a contact book DB here, we assume if user says a name, we try.
        
        # Mock logic for verification:
        # If confidence is high, use WhatsApp.
        
        base_confidence = whatsapp_confidence
        
        # PART 3: QUARANTINE LOGIC
        from Backend.StrategyHealth import StrategyHealth
        health_mgr = StrategyHealth()
        
        if health_mgr.is_quarantined("send_whatsapp"):
            print("[StrategySelector] 'send_whatsapp' is QUARANTINED. Dropping confidence.")
            base_confidence = 0.0 # Force low confidence to trigger gate or fallback selection
            # Alternatively, return fallback immediately, but system uses confidence hierarchy.
            # If we drop to 0, it falls below gate (0.5).
        
        # Apply BIAS
        # goal.target is the target name
        bias = bias_strategy("send_whatsapp", goal.goal_id, goal.target)
        final_confidence = round(base_confidence * bias, 2)
        
        return Strategy(
            strategy_id="send_whatsapp",
            confidence=final_confidence,
            reason=f"Preferred channel. Bias: {bias}",
            fallbacks=["send_sms", "send_email"]
        )

    def _select_open_strategy(self, goal):
        return Strategy(
            strategy_id="open_app_direct",
            confidence=0.9,
            reason="Direct application launch.",
            fallbacks=["search_start_menu"]
        )
