import re

def normalize_text(text: str) -> str:
    """
    Canonical normalization for ALL user input.
    This function must be used exactly once per request.
    """
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation (. , ! ? etc)
    text = re.sub(r"\s+", " ", text)      # collapse spaces
    return text
