from core.modes import RequestMode

def classify(text: str) -> RequestMode:
    t = text.lower().strip()

    # Prioritize ACTION domains (Code, Media, Message)
    if any(k in t for k in (
        "send", "open", "search", "play", "call", "message", "whatsapp",
        "write code", "python", "java", "program", "spotify", "music", "song"
    )):
        return RequestMode.ACTION

    if any(k in t for k in (
        "write", "generate", "explain", "summarize"
    )):
        return RequestMode.CONTENT

    if any(k in t for k in (
        "time", "date", "hello", "hi", "how are you"
    )):
        return RequestMode.GENERAL

    return RequestMode.QUERY
