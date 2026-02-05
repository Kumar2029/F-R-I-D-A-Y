from dataclasses import dataclass
from typing import Optional

@dataclass
class Subgoal:
    id: str
    description: str
    completed: bool = False
    context: Optional[dict] = None # For passing data between subgoals if needed
