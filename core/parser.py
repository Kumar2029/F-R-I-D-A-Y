from core.intents import MediaIntent, CodeIntent, MessageIntent
from core.domains import ActionDomain
import re

def parse_code_intent(text: str) -> CodeIntent:
    t = text.lower()
    
    # 1. Determine Task Type & Code
    # Dynamic generation based on simple keywords
    task_type = "generic"
    code = ""
    filename = "script.py"

    if "hello" in t:
        task_type = "hello_world"
        code = 'print("Hello World")'
        filename = "hello.py"
    elif "triangle" in t:
        task_type = "triangle"
        code = 'n = 5\nfor i in range(1, n+1):\n    print("*" * i)'
        filename = "triangle.py"
    elif "fibonacci" in t:
        task_type = "fibonacci"
        code = 'def fib(n):\n    a, b = 0, 1\n    while a < n:\n        print(a, end=" ")\n        a, b = b, a+b\n    print()\nfib(100)'
        filename = "fibonacci.py"
    elif "series" in t or "numbers" in t:
        task_type = "number_series"
        code = '# Print numbers 1 to 10\nfor i in range(1, 11):\n    print(i)'
        filename = "series.py"
    elif "factorial" in t:
        task_type = "factorial"
        code = 'import math\nprint(f"Factorial of 5 is: {math.factorial(5)}")'
        filename = "factorial.py"
    else:
        # Improved Generic Fallback
        task_type = "script"
        code = f'# Python script for: {text}\nprint("Hello World")'
        filename = "script.py"

    return CodeIntent(
        language="python",
        task_type=task_type,
        code=code,
        filename=filename
    )

def parse_media_intent(text: str) -> MediaIntent:
    # "Play Blinding Lights on Spotify"
    # Extract query
    match = re.search(r"play (.+?)(?: on spotify|$)", text, re.IGNORECASE)
    query = match.group(1).strip() if match else text.replace("play", "").strip()
    
    # Cleanup trailing ' on' if user stopped midway
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
