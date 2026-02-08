from core.context import CTX
from core.modes import RequestMode
# from Backend.Model import FirstLayerDMM # Identifying where content gen lives

def generate_content(text):
    # Stub or call existing backend
    # For now, just a placeholder or call legacy
    # The prompt didn't specify the implementation of generate_content, just the guard.
    # I'll modify this later to call the actual LLM if needed.
    return f"GENERATED CONTENT FOR: {text}"

def handle_content(text: str):
    assert CTX.current_mode == RequestMode.CONTENT, "MODE VIOLATION"

    # Must directly generate content
    # No automation
    # No confirmations
    # No retries

    return generate_content(text)
