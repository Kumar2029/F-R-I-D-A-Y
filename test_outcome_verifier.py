
import sys
import os
import threading
import time
import subprocess

# Ensure root is in path
sys.path.append(os.getcwd())

from Backend.OutcomeVerifier import OutcomeVerifier

def delayed_open_notepad():
    print("Simulating slow app launch (wait 2s)...")
    time.sleep(2)
    print("Opening Notepad now...")
    subprocess.Popen("notepad.exe")

print("Testing OutcomeVerifier Retry Logic...")
verifier = OutcomeVerifier()

# Start notepad in a separate thread with delay
t = threading.Thread(target=delayed_open_notepad)
t.start()

# Verify immediately - should wait and succeed
print("Verifying 'Notepad' window (should wait)...")
start_time = time.time()
success, msg = verifier.verify_outcome({"type": "window_title", "value": "Notepad"})
end_time = time.time()

print(f"Result: {success}")
print(f"Message: {msg}")
print(f"Time taken: {end_time - start_time:.2f}s")

if success and (end_time - start_time) > 1.5:
    print("TEST PASSED: Verifier waited for the window.")
else:
    print("TEST FAILED: Verifier did not wait or failed.")
