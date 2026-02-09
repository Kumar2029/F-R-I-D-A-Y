from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

class ActionDomain(Enum):
    MEDIA = auto()
    CODE = auto()
    ACTION = auto()
    SEARCH = auto()
    CONTENT = auto()
    SYSTEM = auto()

@dataclass
class IntentHints:
    preferred_platform: Optional[str] = None
    last_successful_plan_id: Optional[str] = None
    avoid_strategies: List[str] = field(default_factory=list)
    confidence_boost: float = 0.0

@dataclass
class PlanStats:
    plan_id: str
    domain: str
    success_count: int
    failure_count: int
    last_used: float  # timestamp

@dataclass
class Intent:
    domain: ActionDomain
    action: str
    parameters: Dict[str, Any]
    original_query: str
    confidence: float = 1.0
    hints: Optional[IntentHints] = None

@dataclass
class AutomationAction:
    type: str  # e.g., 'click', 'type', 'wait', 'exec', 'verify'
    params: Dict[str, Any]
    description: str = ""

@dataclass
class VerificationResult:
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class ActionResult:
    success: bool
    message: str
    verification: VerificationResult
    logs: List[str] = field(default_factory=list)

@dataclass
class ExecutionPlan:
    intent: Intent
    steps: List[AutomationAction]
    verification_step: Optional[AutomationAction] = None
    plan_id: str = "default_plan"  # Added for tracking
