JARVIS 2\jarvis-ai-assistant\FRIDAY\generated_code\sum_of_digits.py"
def sum_of_digits(n):
    return sum(int(digit) for digit in str(n))

def main():
    num = 12345
    result = sum_of_digits(num)
    print("Sum of digits of", num, "is:", result)

if __name__ == "__main__":
    main()