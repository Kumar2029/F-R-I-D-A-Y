"D:\JARVIS 2\jarvis-ai-assistant\FRIDAY\generated_code\fibonacci_series.py"
def fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence
n = 10
print(f"Fibonacci series up to {n} terms: {fibonacci(n)}")