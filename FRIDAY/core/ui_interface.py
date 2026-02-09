from typing import Protocol

class UIInterface(Protocol):
    def on_user_input(self, text: str):
        ...

    def on_assistant_output(self, text: str):
        ...
        
    def on_status_change(self, status: str):
        ...
        
    def on_browser_command(self, url: str): # Optional for future
        ...
