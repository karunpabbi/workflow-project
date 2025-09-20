import re


def fix_mermaid(code: str) -> str:
    fixed = []
    for line in code.splitlines():
        # Fix classDef = to :
        if "classDef" in line:
            line = (
                line.replace("fill=", "fill:")
                .replace("stroke=", "stroke:")
                .replace("color=", "color:")
            )
        # Replace parentheses inside square brackets with dashes
        if "[" in line and "]" in line:
            inside = line[line.find("[") + 1 : line.find("]")]
            if "(" in inside or ")" in inside:
                cleaned = inside.replace("(", "-").replace(")", "-")
                line = line[: line.find("[") + 1] + cleaned + line[line.find("]") :]
        fixed.append(line)
    return "\n".join(fixed)


def get_fixed_mermaid_data(text: str) -> str:
    # Regex to capture code block between ```mermaid ... ``` (handles newlines)
    pattern = r"```mermaid\s*\n([\s\S]*?)```"

    def replacer(match):
        original_code = match.group(1).strip()
        fixed_code = fix_mermaid(original_code)
        return f"```mermaid\n{fixed_code}\n```"

    fixed_text, count = re.subn(pattern, replacer, text)

    # If no diagrams found, return a default diagram
    if count == 0:
        default_code = """flowchart TD\nA[No Mermaid diagram found]:::common"""
        return text, f"```mermaid\n{default_code}\n```"

    # Return the fixed text and the last fixed diagram (for compatibility)
    last_fixed = re.findall(pattern, fixed_text)
    last_code = last_fixed[-1] if last_fixed else ""
    return fixed_text, f"```mermaid\n{last_code}\n```"
