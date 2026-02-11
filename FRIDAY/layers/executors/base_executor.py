from abc import ABC, abstractmethod
from typing import List, Tuple
from FRIDAY.core.models import Intent, AutomationAction

class BaseExecutor(ABC):
    @abstractmethod
    def create_play_plan(self, intent: Intent) -> Tuple[List[AutomationAction], AutomationAction]:
        """
        Returns a list of automation steps and a final verification step.
        """
        pass
