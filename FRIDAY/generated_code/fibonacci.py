"D:\JARVIS 2\jarvis-ai-assistant\FRIDAY\generated_code\fibonacci.py"
def generate_fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence
def main():
    n = 10
    fib_sequence = generate_fibonacci(n)
    print(f"The first {n} Fibonacci numbers are: {fib_sequence}")
if __name__ == "__main__":
    main()