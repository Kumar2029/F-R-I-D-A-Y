from typing import List
from FRIDAY.core.models import AutomationAction

class CodeHandler:
    """
    Backend-Driven Code Automation Handler.
    Replaces UI automation with direct file operations and subprocess execution.
    """

    def generate_backend_steps(self, code_content: str, filename: str) -> List[AutomationAction]:
        """
        Generates automation steps for Backend-Driven Code Flow.
        
        Pipeline:
        1. Save Code to File (Backend)
        2. Open File in App (System)
        3. Execute Code (Backend)
        """
        steps = []
        
        # 1. Save File
        steps.append(AutomationAction(
            type="save_code_to_file", 
            params={
                "code": code_content, 
                "filename": filename
            }
        ))
        
        # 2. Open in VS Code (Visual confirmation)
        steps.append(AutomationAction(
            type="open_file_in_vscode", 
            params={} # Path inferred from context
        ))
        
        # 3. Execute Code (Backend verification)
        steps.append(AutomationAction(
             type="execute_python_backend",
             params={} # Path inferred from context
        ))
        
        # 4. Display Output (VS Code Terminal)
        steps.append(AutomationAction(
             type="run_in_vscode_terminal",
             params={} # Path inferred from context
        ))

        return steps

    def get_verification_step(self, filename: str) -> AutomationAction:
        # Verification is now implicitly handled by 'execute_python_backend' returning True/False
        # But we can add a final "Success" message step if needed.
        # The planner asks for a verification step.
        # We can use a dummy verification or a "speak success" verification?
        # Actually, "Step 7 -> Report success or failure".
        # If automation fails, it reports failure.
        # If it succeeds, we want to VERIFY it succeeded.
        # 'execute_python_backend' ALREADY verifies return code.
        
        return AutomationAction(
             type="verify_success_signal",
             params={"message": "Back-end execution successful"}
        )
