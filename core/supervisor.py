from core.context import CTX
from core.classifier import classify
from core.modes import RequestMode

from handlers.general import handle_general
from handlers.content import handle_content
from handlers.action import handle_action
from handlers.query import handle_query

def supervise(user_text: str):
    mode = classify(user_text)

    CTX.current_mode = mode
    CTX.raw_text = user_text

    if mode == RequestMode.GENERAL:
        return handle_general(user_text)

    if mode == RequestMode.CONTENT:
        return handle_content(user_text)

    if mode == RequestMode.ACTION:
        return handle_action(user_text)

    return handle_query(user_text)
