import sys
import os
import traceback
from PyQt5.QtCore import QThread, pyqtSignal

# Ensure root is in path to import FRIDAY
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from FRIDAY.main import FridayOrchestrator
from FRIDAY.core.ui_interface import UIInterface

class FridayWorker(QThread): # Removed explicit UIInterface inheritance to avoid metaclass conflict

    # Signals to update UI
    signal_user_input = pyqtSignal(str)
    signal_assistant_output = pyqtSignal(str)
    signal_status_change = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.orchestrator = None
        self.running = True

    def run(self):
        try:
            # Initialize Orchestrator with SELF as the UI interface
            self.orchestrator = FridayOrchestrator(ui=self)
            self.signal_status_change.emit("FRIDAY System Initializing...")
            self.orchestrator.start()
        except Exception as e:
            self.signal_status_change.emit(f"Critical Error: {e}")
            traceback.print_exc()

    def stop(self):
        if self.orchestrator:
            self.orchestrator.running = False
        self.quit()
        self.wait()

    # UIInterface Implementation
    def on_user_input(self, text: str):
        self.signal_user_input.emit(text)

    def on_assistant_output(self, text: str):
        self.signal_assistant_output.emit(text)

    def on_status_change(self, status: str):
        self.signal_status_change.emit(status)
