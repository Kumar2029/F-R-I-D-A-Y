from dataclasses import dataclass

@dataclass
class MediaIntent:
    action: str        # play / pause / next
    platform: str      # spotify
    query: str         # "blinding lights"

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
