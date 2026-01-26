
import time
from rich import print

class ContextEngine:
    def __init__(self):
        # Behavioral Constraints (0.0 to 1.0)
        self.context = {
            "autonomy_level": 0.5,        # 1.0 = Full Auto, 0.0 = Ask everything
            "interaction_speed": 0.5,     # 1.0 = Fast/Brief, 0.0 = Slow/Detailed
            "verbosity_level": 0.5,       # 1.0 = Chatty, 0.0 = Silent
            "confirmation_threshold": 0.5,# 1.0 = Paranoiac, 0.0 = YOLO
            "surprise_tolerance": 0.5     # 1.0 = Anything goes, 0.0 = Strict
        }
        
        self.last_update = time.time()
        
        # Decay Config (Per second)
        # Context tends to drift back to "Neutral" (0.5) over time
        self.decay_rate = 0.005 
        
        # Baselines
        self.baselines = {k: 0.5 for k in self.context}
        # Custom baselines
        self.baselines["autonomy_level"] = 0.4 # Default to slightly cautious
        self.baselines["surprise_tolerance"] = 0.3 # Default to low tolerance (safe)

    def _decay_context(self):
        """Passive decay towards baseline."""
        now = time.time()
        delta = now - self.last_update
        
        for key, val in self.context.items():
            baseline = self.baselines[key]
            
            # Simple linear decay
            if val > baseline:
                self.context[key] = max(baseline, val - (self.decay_rate * delta))
            elif val < baseline:
                self.context[key] = min(baseline, val + (self.decay_rate * delta))
                
        self.last_update = now

    def update_context(self, signal_type, intensity=0.1, source="behavior"):
        """
        Fuse a new signal into the context.
        Signal Types: 
            - behavior: repetition, abort, correction, silence
            - environment: failure, success, time
        """
        self._decay_context()
        
        # --- FUSION LOGIC ---
        
        # 1. Negative User Signals (Reduce Autonomy/Trust)
        if signal_type in ["repetition", "abort", "correction"]:
            # Drop autonomy significantly
            self.context["autonomy_level"] -= (0.15 * intensity)
            # Increase confirmation needed
            self.context["confirmation_threshold"] += (0.15 * intensity)
            # Lower surprise tolerance (be predictable)
            self.context["surprise_tolerance"] -= (0.2 * intensity)
            
            if signal_type == "repetition":
                # User is impatient -> Speed up, shut up
                self.context["interaction_speed"] += (0.1 * intensity)
                self.context["verbosity_level"] -= (0.2 * intensity)

        # 2. Positive/Success Signals
        elif signal_type == "success":
            # Build trust slowly
            self.context["autonomy_level"] += (0.05 * intensity)
            self.context["confirmation_threshold"] -= (0.05 * intensity)
            self.context["surprise_tolerance"] += (0.05 * intensity)
            
        # 3. System Failures
        elif signal_type == "failure":
             # Big hit to autonomy and tolerance
            self.context["autonomy_level"] -= (0.2 * intensity)
            self.context["surprise_tolerance"] = 0.1 # Collapse tolerance
            self.context["interaction_speed"] -= 0.1 # Slow down (to think/debug)

        # 4. Decisive User
        elif signal_type == "decisive_command":
            self.context["interaction_speed"] += (0.1 * intensity)
            self.context["verbosity_level"] -= (0.1 * intensity)

        # --- CLAMPING ---
        for k in self.context:
            self.context[k] = max(0.0, min(1.0, self.context[k]))
            
        # Logging changes
        # print(f"[ContextEngine] Updated: {self.format_context()}")

    def get_context(self):
        self._decay_context()
        return self.context.copy()

    def format_context(self):
        c = self.get_context()
        return (f"Autonomy:{c['autonomy_level']:.2f} | "
                f"Speed:{c['interaction_speed']:.2f} | "
                f"SurpriseTol:{c['surprise_tolerance']:.2f}")

if __name__ == "__main__":
    ce = ContextEngine()
    print("Init:", ce.format_context())
    
    print("\nEvent: Abort!")
    ce.update_context("abort", 1.0)
    print("Post-Abort:", ce.format_context())
    
    print("\nEvent: Success x 5")
    for _ in range(5):
        ce.update_context("success", 1.0)
    print("Post-Success:", ce.format_context())
