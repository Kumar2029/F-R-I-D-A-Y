from dataclasses import dataclass
from typing import Optional

@dataclass
class Outcome:
    success: bool
    reason: Optional[str] = None
    evidence: Optional[str] = None
