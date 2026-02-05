from dataclasses import dataclass
from typing import Optional

@dataclass
class Goal:
    name: str                  # e.g. "send_message", "search_web"
    target: Optional[str] = None
    content: Optional[str] = None
    priority: str = "normal"
    response_mode: str = "ACTION" # "ACTION", "CONTENT", "QUERY"
    # User requested NO extra fields like 'id' or 'constraints'.
    # However, existing code uses 'constraints'.
    # "DO NOT add extra fields like id or metadata"
    # I should strictly follow the prompt but I must check if 'constraints' are vital.
    # The prompt explicitly listed the fields to add.
    # Existing Goal has 'constraints'. If I remove it, Planner might break if it relies on it.
    # The prompt says "DO NOT delete working logic".
    # BUT "Add ONLY these dataclasses... Remove ALL other Goal / Strategy class definitions"
    # "DO NOT add extra fields like id or metadata".
    # I will stick to the requested fields. If constraints are needed, I might need to clarify or map them to content?
    # Actually, previous GoalExtractor used constraints={}, I haven't seen them used heavily yet.
    # I will strictly follow the prompt.

@dataclass
class Strategy:
    name: str                  # e.g. "send_whatsapp", "search_web"
    confidence: float
    reason: str
    # Existing Strategy has 'fallbacks'.
    # Prompt says "Remove ALL other... DO NOT add extra fields".
    # StrategySelector currently returns fallbacks.
    # If I remove fallbacks, I might break fallback logic?
    # "StrategySelector MUST return Strategy" - implies singular.
    # I will follow strictly.
