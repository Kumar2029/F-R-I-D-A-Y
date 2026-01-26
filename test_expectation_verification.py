from Backend.ExpectationModel import ExpectationModel

def test_mismatch_logic():
    print("Testing Mismatch Logic for send_whatsapp...")
    em = ExpectationModel()
    
    # Simulate "Send message..." query
    exp = em.infer_expectation("Send message to Mom")
    
    # Simulate Plan with send_whatsapp
    plan = [{"action": "send_whatsapp", "target": "Mom | Hello"}]
    
    score, reasons = em.detect_belief_mismatch(plan, exp)
    
    print(f"Expectation Scope: {exp['expected_scope']}")
    print(f"Plan Actions: {[s['action'] for s in plan]}")
    print(f"Mismatch Score: {score}")
    print(f"Reasons: {reasons}")
    
    if score == 0.0:
        print("SUCCESS: No mismatch detected.")
    else:
        print("FAILURE: Mismatch detected.")

if __name__ == "__main__":
    test_mismatch_logic()
