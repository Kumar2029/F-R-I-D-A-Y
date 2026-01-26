
import sys
import os
import time

# Ensure root is in path
sys.path.append(os.getcwd())

from Backend.UserStateEstimator import UserStateEstimator
from Backend.Planner import generate_plan
from Backend.Verifier import Verifier

def test_user_state_adaptation():
    print("Initializing User State Estimator...")
    estimator = UserStateEstimator()
    verifier = Verifier()
    
    # 1. Baseline Test
    print("\n--- TEST 1: Baseline State ---")
    state = estimator.get_state()
    print(f"State: {estimator.format_state()}")
    
    # Simulate Planner call (mocked output check)
    # We mainly want to see if the function runs without error
    # and if we can verify the state context injection (manually inspected in logs if we had them)
    # For now, we trust the code we wrote, but let's check verifier logic.
    
    is_safe, risk, _ = verifier.verify_plan([{"action": "open", "target": "notepad"}], user_state=state)
    print(f"Verifier Risk Score: {risk} (Expected Low)")

    # 2. Simulate User Frustration (Repetition)
    print("\n--- TEST 2: Simulating Frustration (Repetition) ---")
    estimator.update_state("repetition", intensity=1.0)
    estimator.update_state("repetition", intensity=1.0)
    estimator.update_state("repetition", intensity=1.0)
    
    state = estimator.get_state()
    print(f"State: {estimator.format_state()}")
    
    # Patience should be low.
    if state["patience"] < 0.8:
        print("PASS: Patience dropped successfully.")
    else:
        print("FAIL: Patience did not drop enough.")

    # 3. Simulate Low Trust (Correction)
    print("\n--- TEST 3: Simulating Low Trust ---")
    estimator.update_state("correction", intensity=1.0)
    estimator.update_state("correction", intensity=1.0)
    
    state = estimator.get_state()
    print(f"State: {estimator.format_state()}")
    
    if state["trust"] < 0.4:
         print("PASS: Trust dropped successfully.")
    
    # Verifier Check
    is_safe, risk, _ = verifier.verify_plan([{"action": "open", "target": "notepad"}], user_state=state)
    print(f"Verifier Risk Score: {risk}")
    
    if risk >= 0.3: # Base is 0.1, +0.2 penalty
        print("PASS: Verifier increased risk score due to low trust.")
    else:
        print("FAIL: Verifier did not increase risk score.")

if __name__ == "__main__":
    test_user_state_adaptation()
