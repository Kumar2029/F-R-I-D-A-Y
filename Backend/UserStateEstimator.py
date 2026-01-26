
import time
from rich import print

class UserStateEstimator:
    def __init__(self):
        # Continuous Probabilities (0.0 to 1.0)
        self.state = {
            "patience": 1.0,       # Starts high
            "trust": 0.5,          # Starts neutral
            "arousal": 0.2,        # Starts calm
            "overload_risk": 0.1,  # Starts low
            "confidence": 0.5      # System confidence
        }
        
        self.last_update = time.time()
        self.history = []
        
        # Decay rates (per second) - slowly drift to baseline
        self.decay_rates = {
            "patience": 0.005,      # Recover slowly
            "trust": 0.001,         # Trust takes time to build/lose
            "arousal": 0.02,        # Calm down relatively fast
            "overload_risk": 0.01   # Recover from overload
        }
        
        # Baselines
        self.baselines = {
            "patience": 1.0,
            "trust": 0.5,
            "arousal": 0.2,
            "overload_risk": 0.1
        }

    def _decay_state(self):
        """Apply passive decay to all states toward baseline."""
        now = time.time()
        delta = now - self.last_update
        
        for key, val in self.state.items():
            if key == "confidence": continue
            
            baseline = self.baselines[key]
            rate = self.decay_rates.get(key, 0.0)
            
            if val > baseline:
                self.state[key] = max(baseline, val - (rate * delta))
            elif val < baseline:
                self.state[key] = min(baseline, val + (rate * delta))
                
        self.last_update = now

    def update_state(self, signal_type, intensity=0.1):
        """
        Update state based on a signal.
        signal_type: 'repetition', 'abort', 'correction', 'forceful', 'failure', 'success'
        intensity: 0.0 to 1.0 magnitude of the event
        """
        self._decay_state()
        history_entry = {"time": time.time(), "signal": signal_type, "intensity": intensity}
        self.history.append(history_entry)
        
        # Keep history short
        if len(self.history) > 20:
            self.history.pop(0)

        prev_state = self.state.copy()

        # --- UPDATE RULES ---
        
        if signal_type == "repetition":
            # Repetition kills patience and trust
            self.state["patience"] -= (0.15 * intensity)
            self.state["arousal"] += (0.1 * intensity)
            
        elif signal_type == "abort" or signal_type == "stop":
            # Aborting suggests error or frustration
            self.state["patience"] -= (0.2 * intensity)
            self.state["trust"] -= (0.1 * intensity)
            self.state["arousal"] += (0.1 * intensity)
            
        elif signal_type == "correction":
            # User correcting the AI means low trust in current path
            self.state["trust"] -= (0.15 * intensity)
            self.state["confidence"] -= 0.2 
            
        elif signal_type == "forceful":
            # "JUST DO IT"
            self.state["arousal"] += (0.3 * intensity)
            self.state["patience"] -= (0.1 * intensity)
            
        elif signal_type == "failure":
            # System failure
            self.state["trust"] -= (0.2 * intensity)
            self.state["overload_risk"] += (0.15 * intensity)
            
        elif signal_type == "success":
            # Success rebuilds trust and patience
            self.state["trust"] += (0.05 * intensity)
            self.state["patience"] += (0.1 * intensity)
            self.state["overload_risk"] -= (0.1 * intensity)
            self.state["confidence"] += 0.1

        # --- CLAMP VALUES (0.0 to 1.0) ---
        for k in self.state:
            self.state[k] = max(0.0, min(1.0, self.state[k]))

        # Debug Log (only if significant change)
        if any(abs(self.state[k] - prev_state[k]) > 0.05 for k in self.state):
             print(f"[UserStateEstimator] Updated: {self.format_state()}")

    def get_state(self):
        self._decay_state()
        return self.state

    def format_state(self):
        return f"Patience:{self.state['patience']:.2f} Trust:{self.state['trust']:.2f} Risk:{self.state['overload_risk']:.2f}"

if __name__ == "__main__":
    # Test
    est = UserStateEstimator()
    print("Initial:", est.format_state())
    
    print("\nEvent: Repeated Command")
    est.update_state("repetition", 1.0)
    
    print("\nEvent: Failure")
    est.update_state("failure", 1.0)
    
    print("\nWait 2s decay...")
    time.sleep(2)
    print("After decay:", est.format_state())
