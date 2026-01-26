import re

SUPPORTED_PREFIXES = (
    "open ",
    "close ",
    "type ",
    "press ",
    "search_web ",
    "google search ",
    "youtube search ",
    "play ",
    "system ",
    "send_whatsapp ",
    "wait ",
    "content ", # Added based on Automation.py support
    "generate_image " # Added for explicit support if already compiled
)

def compile_command(command: str) -> str:
    command = command.strip().lower()

    # IMAGE GENERATION (ABSOLUTE OVERRIDE)
    # Checks raw command for natural language "generate image of..."
    if command.startswith("generate") and "image" in command:
        prompt = re.sub(r"generate( an| a)? image( of)?", "", command).strip()
        # Normalize to canonical
        return f"generate_image {prompt}"

    for prefix in SUPPORTED_PREFIXES:
        if command.startswith(prefix):
            return command  # PASS THROUGH UNTOUCHED

    # Special case: generate_image might be a prefix itself in canonical form
    if command.startswith("generate_image "):
        return command

    raise ValueError(f"Unsupported command: {command}")

def compile_commands(commands: list[str]) -> list[str]:
    """
    HARD NORMALIZER.
    Ensures execution layer ONLY sees canonical commands.
    """
    compiled = []

    for cmd in commands:
        try:
             compiled.append(compile_command(cmd))
        except ValueError as e:
             # Log but do not crash? The user said "except ValueError as e: print...".
             # But we need to decide if we drop it or prefix it.
             # User said: "Fail ONLY when a command is truly unsupported"
             # And "Remove the __INVALID__ command prefix mechanism"
             # And "Prevent false 'Objective met' reports on failure"
             
             # If we drop it, the list is empty?
             raise RuntimeError(f"Unsupported command from Planner: {cmd}")

    return compiled
