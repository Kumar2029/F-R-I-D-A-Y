from enum import Enum, auto

class RequestMode(Enum):
    GENERAL = auto()
    CONTENT = auto()
    ACTION  = auto()
    QUERY   = auto()
