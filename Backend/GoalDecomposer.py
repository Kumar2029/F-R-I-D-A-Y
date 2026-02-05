from Backend.contracts import Goal
from Backend.Subgoal import Subgoal
import uuid

class GoalDecomposer:
    def decompose(self, goal: Goal) -> list[Subgoal]:
        """
        Decomposes a high-level Goal into a list of atomic Subgoals.
        Determinstic, rule-based.
        """
        steps = []
        
        if goal.name == "send_message":
            # Atomic Goal: Pass through with natural language reconstruction
            desc = f"send message to {goal.target}"
            if goal.content:
                desc += f" saying {goal.content}"
            
            steps.append(Subgoal(
                id=str(uuid.uuid4()),
                description=desc
            ))

        elif goal.name == "open_application":
            steps.append(Subgoal(
                id=str(uuid.uuid4()),
                description=f"open {goal.target}"
            ))

        elif goal.name == "search_web":
             # "search for" triggers the search intent in GoalExtractor
             steps.append(Subgoal(
                id=str(uuid.uuid4()),
                description=f"search for {goal.target}"
            ))
            
        elif goal.name == "generate_image":
             # Pattern: "generate image of [content]"
             steps.append(Subgoal(
                id=str(uuid.uuid4()),
                description=f"generate image of {goal.content}"
            ))

        elif goal.name in ["write_code", "explain", "pattern", "story"] or goal.content:
             # Fallback: Map all content-heavy or unsure requests to generate_content
             steps.append(Subgoal(
                id=str(uuid.uuid4()),
                description=f"generate content about {goal.content if goal.content else goal.name}"
            ))

        else:
            # Absolute Fallback (Unsure?) -> Content
            steps.append(Subgoal(
                id=str(uuid.uuid4()),
                description=f"generate content about {goal.name}"
            ))
            
        return steps
