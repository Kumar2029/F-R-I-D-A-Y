import sys
import os

# Ensure root is in path
sys.path.append(os.getcwd())

from FRIDAY.core.utils import code_cleanup

def test_cleanup():
    input_code = r"""\JARVIS 2\jarvis-ai-assistant\FRIDAY\generated_code\fibonacci_series.py"
def fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence
def print_fibonacci(n):
    fib_sequence = fibonacci(n)
    print(f"The first {n} numbers in the Fibonacci sequence are: {fib_sequence}")
print_fibonacci(10)"""

    print("--- Input Code ---")
    print(input_code)
    print("------------------")

    cleaned = code_cleanup.clean_generated_code(input_code)
    
    print("\n--- Cleaned Code ---")
    print(cleaned)
    print("--------------------")
    
    # Check if first line remains
    lines = cleaned.split('\n')
    if "JARVIS" in lines[0]:
        print("FAIL: First line still contains path artifact.")
    else:
        print("PASS: Artifact removed.")

if __name__ == "__main__":
    test_cleanup()
