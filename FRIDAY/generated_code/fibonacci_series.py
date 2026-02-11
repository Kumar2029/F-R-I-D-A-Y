"D:\JARVIS 2\jarvis-ai-assistant\FRIDAY\generated_code\fibonacci_series.py"
def fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence
def print_fibonacci(n):
    fib_sequence = fibonacci(n)
    print(f"The first {n} numbers in the Fibonacci sequence are: {fib_sequence}")
print_fibonacci(10)