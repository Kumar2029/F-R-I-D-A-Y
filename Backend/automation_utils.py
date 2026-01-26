
import time
from rich import print

def wait_until(condition_fn, timeout=5.0, interval=0.1, on_fail_reason=None):
    """
    Polls condition_fn() repeatedly until it returns True or timeout expires.
    Returns True if condition met, False otherwise.
    """
    start_time = time.time()
    
    # Optional debug log
    # print(f"[Wait] Starting wait for {condition_fn.__name__} (Timeout: {timeout}s)")
    
    while time.time() - start_time < timeout:
        try:
            if condition_fn():
                # print(f"[Wait] Condition {condition_fn.__name__} satisfied.")
                return True
        except Exception as e:
            print(f"[Wait] Check failed with error: {e}")
            
        time.sleep(interval)
        
    print(f"[Wait] Timed out waiting for: {on_fail_reason or condition_fn.__name__}")
    return False
