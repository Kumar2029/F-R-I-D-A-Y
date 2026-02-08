from core.context import CTX
from core.modes import RequestMode

def ask_for_clarification():
    return "Could you clarify your request?"

def handle_query(text: str):
    assert CTX.current_mode == RequestMode.QUERY, "MODE VIOLATION"

    return ask_for_clarification()
