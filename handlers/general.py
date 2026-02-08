from core.context import CTX
from core.modes import RequestMode
from Backend.Chatbot import ChatBot  # Assuming ChatBot handles general/chitchat

def handle_general(text: str):
    assert CTX.current_mode == RequestMode.GENERAL, "MODE VIOLATION"
    
    # Reuse existing ChatBot logic for general conversation
    # Or simple print for now if ChatBot is not imported correctly
    return ChatBot(text)
