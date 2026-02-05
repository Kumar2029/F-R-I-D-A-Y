from Backend.contracts import Goal, Strategy

class GSOAdapter:
    @staticmethod
    def convert_to_commands(goal: Goal, strategy: Strategy) -> list[str]:
        """
        Direct deterministic conversion from Goal+Strategy to commands.
        Bypasses Planner for strict intents.
        """
        if strategy.name == "send_whatsapp":
            # Strict contract: target is contact, content is message
            if not goal.target or not goal.content:
                 raise ValueError("send_whatsapp requires target and content")
            return [f"send_whatsapp {goal.target} | {goal.content}"]
        
        if strategy.name == "search_web":
            return [f"search_web {goal.target}"]
            
        if strategy.name == "open_app_direct":
             return [f"open {goal.target}"]
             
        if strategy.name == "generate_image_local":
             return [f"generate_image {goal.content}"]
             
        # Fallback to planner? 
        # Or raise error? Prompt says "NEVER accepts raw strings".
        # This method accepts Goal/Strategy.
        return []

    @staticmethod
    def plan_to_commands(plan: list[dict]) -> list[str]:
        """
        Converts GSO planner steps into legacy Automation commands.
        MUST remain deterministic and backward compatible.
        """
        commands = []
        
        # Determine strict plan list from input (handle wrapper dict if present)
        steps = plan.get("plan", []) if isinstance(plan, dict) else plan

        for step in steps:
            action = step.get("action")
            target = step.get("target", "")

            if action == "open":
                commands.append(f"open {target}")

            elif action == "send_whatsapp":
                # Check formatting
                if "|" in target:
                    parts = target.split("|")
                    contact = parts[0].strip()
                    message = parts[1].strip()
                    commands.append(f"send_whatsapp {contact} | {message}")
                else:
                    contact = step.get("contact")
                    message = step.get("message")
                    if not contact and "|" in target:
                         parts = target.split("|")
                         contact = parts[0].strip()
                         message = parts[1].strip()
                    
                    commands.append(f"send_whatsapp {contact} | {message}")

            elif action == "type":
                commands.append(f"type {target}")

            elif action == "press":
                commands.append(f"press {target}")

            elif action == "close":
                commands.append(f"close {target}")

            elif action == "system":
                commands.append(f"system {target}")
            
            elif action == "generate_image":
                commands.append(f"generate_image {target}")
            
            elif action == "search_web":
                commands.append(f"search_web {target}")

            else:
                 commands.append(f"{action} {target}")

        return commands

