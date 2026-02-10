from Backend.CommandCompiler import compile_commands

def test_strict_compiler():
    print("--- Testing Strict Compiler ---")
    
    # Positive Case
    try:
        cmds = compile_commands(["open notepad"])
        print(f"Success: 'open notepad' passed -> {cmds}")
    except Exception as e:
        print(f"FAILED: 'open notepad' raised {e}")

    # Negative Case
    try:
        compile_commands(["dance_on_table"])
        print("FAILED: 'dance_on_table' should have raised RuntimeError")
    except RuntimeError as e:
        print(f"Success: Caught expected error -> {e}")
    except Exception as e:
        print(f"FAILED: Wrong error type -> {type(e)}")

if __name__ == "__main__":
    test_strict_compiler()