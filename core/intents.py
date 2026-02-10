from dataclasses import dataclass

@dataclass
@dataclass
class MediaIntent:
    action: str        # play / pause / next
    query: str         # "blinding lights"
    domain: str = "MEDIA"
    platform_hint: str = None # "spotify", "youtube", "local", or None
    confidence: float = 1.0

@dataclass
class CodeIntent:
    language: str
    task: str
    generated_code: str
    filename: str

@dataclass
class MessageIntent:
    contact: str
    message: str
