from dataclasses import dataclass
from core.domains import ActionDomain

@dataclass
class MediaIntent:
    platform: str
    action: str
    query: str
    confidence: float = 1.0

@dataclass
class CodeIntent:
    language: str
    task_type: str
    code: str
    filename: str
    confidence: float = 1.0

@dataclass
class MessageIntent:
    contact: str
    message: str
    confidence: float = 1.0
