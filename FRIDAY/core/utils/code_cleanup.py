import ast
import re

def clean_generated_code(code: str) -> str:
    """
    Cleans up LLM generated code by stripping artifacts like filenames,
    markdown blocks, and other common non-code headers.
    Uses AST parsing to verify validity.
    """
    # 1. Basic Markdown Cleanup
    code = code.replace("```python", "").replace("```", "").strip()
    
    # 2. Heuristic Line Skipping
    lines = code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        sline = line.strip().lower()
        if not sline:
            continue
            
        # Explicitly skip filename-like lines
        # "python d:\path\to\file.py"
        # "filename: foo.py"
        # "here is the code:"
        
        # Regex for common garbage patterns
        # Starts with "python " and has quotes or path chars
        if sline.startswith("python ") and ("\"" in sline or "'" in sline or "\\" in sline):
            continue
            
        if sline.endswith(".py") or sline.endswith(".py\"") or sline.endswith(".py'"):
            continue
            
        if sline.startswith("filename:") or sline.startswith("file:"):
            continue
            
        if "here is the code" in sline:
            continue

        cleaned_lines.append(line)

    cleaned_code = '\n'.join(cleaned_lines).strip()
    
    # 3. AST-Based Verification Loop
    # Try parsing. If fail, strip 1 line (up to 5 times)
    current_code = cleaned_code
    for attempt in range(6):
        try:
            ast.parse(current_code)
            return current_code
        except SyntaxError:
            # Strip first line
            lines = current_code.split('\n')
            if len(lines) > 1:
                current_code = '\n'.join(lines[1:]).strip()
            else:
                break
    
    # If all failed, return error comment
    return f"# Error: Generated code had syntax errors that could not be cleaned.\n# Original:\n{code}"
