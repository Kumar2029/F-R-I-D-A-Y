import json
import os
from Backend.contracts import Strategy
from Backend.StrategyHealth import StrategyHealthManager

class StrategySelector:
    def __init__(self, outcome_manager=None):
        self.health_manager = StrategyHealthManager()
        # outcome_manager kept for legacy compatibility if passed, but logic moved to HealthManager

    def _rank_candidates(self, candidates: list[Strategy]) -> list[Strategy]:
        """
        Ranks strategies by Health Score (DESC).
        """
        # Annotate with scores
        scored = []
        for s in candidates:
            health = self.health_manager.get_health(s.name)
            # Log score for debugging
            # print(f"[StrategySelector] Candidate {s.name}: Score {health.score:.2f}")
            scored.append((s, health.score))
        
        # Sort by Score DESC
        # Stable sort preserves original order priority for ties
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [s for s, score in scored]

    def select_strategy(self, goal, user_state=None):
        """
        Choose how to fulfill a goal using adaptive health scoring.
        """
        if not goal or not hasattr(goal, 'name'):
            return Strategy(name="ask_user", confidence=1.0, reason="Invalid Goal Object")

        candidates = []

        # 1. GENERATE CANDIDATES
        if goal.name == "send_message":
            # Primary: WhatsApp
            candidates.append(Strategy(
                name="send_whatsapp",
                confidence=0.8, # Base confidence
                reason="Preferred messaging channel"
            ))
            # Secondary: SMS (Mock/Placeholder if implemented in future)
            # For now, just one candidate to test "De-prioritization/Fail-stop" logic.
            
        elif goal.name == "open_application":
            candidates.append(Strategy(
                name="open_app_direct",
                confidence=0.9,
                reason="Direct launch"
            ))
            
        elif goal.name == "search_web":
            candidates.append(Strategy(
                name="search_web", 
                confidence=0.95, 
                reason="Standard web search"
            ))

        elif goal.name == "generate_image":
            candidates.append(Strategy(
                name="generate_image_local",
                confidence=0.95,
                reason="Local Stable Diffusion"
            ))
            
        else:
            return Strategy(name="ask_user", confidence=1.0, reason="Clarification required")

        # 2. ADAPTIVE RANKING
        ranked = self._rank_candidates(candidates)
        
        if not ranked:
            return Strategy(name="ask_user", confidence=1.0, reason="No strategies available")

        # 3. FAIL-SAFE GUARDRAILS (v4 UNFREEZE)
        best_strategy = ranked[0]
        best_health = self.health_manager.get_health(best_strategy.name)
        
        # Unfreeze Logic: Strategies degrade, they don't lock immediately.
        # Only block if health is critically low AND we have tried multiple times recently.
        # Note: Health score drops with failures.
        
        if best_health.score < 0.3:
            if best_health.failures < 3:
                print(f"[StrategySelector] WARNING: Low score ({best_health.score:.2f}) but failures < 3. Allowing RETRY.")
                # We return the strategy but maybe log a warning
                return best_strategy
            else:
                 print(f"[StrategySelector] CRITICAL: Top strategy {best_strategy.name} failed too many times ({best_health.failures}). Stopping.")
                 return Strategy(
                     name="ask_user", 
                     confidence=1.0, 
                     reason=f"System unreliable for {goal.name} (Score: {best_health.score:.2f}). Please confirm or provide guidance."
                 )

        print(f"[StrategySelector] Selected {best_strategy.name} with Score {best_health.score:.2f}")
        return best_strategy

    def _select_message_strategy(self, goal):
        # Legacy stub to prevent breaking if called directly (though select_strategy routes elsewhere now)
        return self.select_strategy(goal) # Redirect
    
    def _select_open_strategy(self, goal):
        return self.select_strategy(goal)
