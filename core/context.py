from core.modes import RequestMode

class ExecutionContext:
    current_mode: RequestMode | None = None
    raw_text: str = ""

CTX = ExecutionContext()
