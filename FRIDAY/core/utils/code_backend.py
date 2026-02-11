import os
import subprocess
import sys
from datetime import datetime
from typing import Tuple, Optional

BASE_CODE_DIR = os.path.join(os.getcwd(), "FRIDAY", "generated_code")

def create_code_file(code: str, filename: str) -> str:
    """
    Creates a python file with the given code content in the generated_code directory.
    Returns the full absolute path.
    """
    if not os.path.exists(BASE_CODE_DIR):
        os.makedirs(BASE_CODE_DIR)

    # Clean filename to ensure .py extension
    if not filename.endswith(".py"):
        filename += ".py"
        
    full_path = os.path.join(BASE_CODE_DIR, filename)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)

    return full_path

def open_file_in_vscode(file_path: str):
    """
    Opens the file in VS Code using the 'code' command.
    """
    try:
        # Popen doesn't block
        subprocess.Popen(["code", file_path], shell=True)
    except Exception as e:
        print(f"[Backend] Failed to open VS Code: {e}")

def execute_python_file(file_path: str) -> Tuple[int, str, str]:
    """
    Executes a python file using the current sys.executable.
    Returns (returncode, stdout, stderr).
    """
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=30 # Safety timeout for scripts
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Execution timed out (30s limit)."
    except Exception as e:
        return -1, "", str(e)
