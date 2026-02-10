from FRIDAY.core.models import Intent, ActionDomain

class DomainRouter:
    """
    Strictly accepts an Intent and returns the appropriate Planner Class Name.
    No ambiguity allowed.
    """
    def route(self, intent: Intent) -> str:
        if not isinstance(intent, Intent):
            raise TypeError(f"Router expected Intent object, got {type(intent)}")

        # Strict Mapping
        match intent.domain:
            case ActionDomain.MEDIA:
                return "MediaPlanner"
            case ActionDomain.CODE:
                return "CodePlanner"
            case ActionDomain.SYSTEM:
                return "ActionPlanner" # Fallback/Diagnostics
            case ActionDomain.ACTION:
                # Sub-routing based on action type
                action = intent.action.lower()
                if "whatsapp" in action or "message" in action or "send" in action or "email" in action:
                    return "CommunicationPlanner"
                return "ActionPlanner" # Default for open/close/volume
            case ActionDomain.CONTENT:
                return "GeneralPlanner"
            case ActionDomain.SEARCH:
                return "WebPlanner" 
            case ActionDomain.GENERAL:
                return "GeneralPlanner"
            case _:
                raise ValueError(f"No planner mapped for domain: {intent.domain}")
