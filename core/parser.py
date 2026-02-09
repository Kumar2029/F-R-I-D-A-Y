from core.intents import MediaIntent, CodeIntent, MessageIntent
import re

def parse_code_intent(text: str) -> CodeIntent:
    t = text.lower()
    
    # 1. Determine Task Type & Code
    task = "generic"
    generated_code = ""
    filename = "script.py"

    if "hello" in t:
        task = "hello_world"
        generated_code = 'print("Hello World")'
        filename = "hello.py"
    elif "triangle" in t:
        task = "triangle"
        generated_code = 'n = 5\nfor i in range(1, n+1):\n    print("*" * i)'
        filename = "triangle.py"
    elif "fibonacci" in t:
        task = "fibonacci"
        generated_code = 'def fib(n):\n    a, b = 0, 1\n    while a < n:\n        print(a, end=" ")\n        a, b = b, a+b\n    print()\nfib(100)'
        filename = "fibonacci.py"
    elif "series" in t or "numbers" in t:
        task = "number_series"
        generated_code = '# Print numbers 1 to 10\nfor i in range(1, 11):\n    print(i)'
        filename = "series.py"
    elif "factorial" in t:
        task = "factorial"
        generated_code = 'import math\nprint(f"Factorial of 5 is: {math.factorial(5)}")'
        filename = "factorial.py"
    else:
        # Default / Generic
        task = "generic"
        generated_code = f'# Python script for: {text}\nprint("Running generic script...")'
        filename = "script.py"

    return CodeIntent(
        language="python",
        task=task,
        generated_code=generated_code,
        filename=filename
    )

def parse_media_intent(text: str) -> MediaIntent:
    # "Play Blinding Lights on Spotify"
    # Extract query
    match = re.search(r"play (.+?)(?: on spotify|$)", text, re.IGNORECASE)
    query = match.group(1).strip() if match else text.replace("play", "").strip()
    
    # Cleanup trailing ' on'
    if query.lower().endswith(" on"):
        query = query[:-3].strip()
        
    return MediaIntent(
        platform="spotify",
        action="play",
        query=query
    )

def parse_message_intent(text: str) -> MessageIntent:
    # "Message to Vasanth saying hello"
    match = re.search(r"message to (.+?) saying (.+)", text, re.IGNORECASE)
    if match:
        return MessageIntent(contact=match.group(1).strip(), message=match.group(2).strip())
    
    match = re.search(r"message to (.+)", text, re.IGNORECASE)
    if match:
        return MessageIntent(contact=match.group(1).strip(), message=" ")
        
    return MessageIntent(contact="Unknown", message="")
