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
    # Regex to capture code block between ```mermaid ... ```
    pattern = r"```mermaid(.*?)```"
    matches = re.findall(pattern, text, flags=re.DOTALL)

    fixed_text = text
    fixed_code = """
    flowchart TD
    A[No Mermaid diagram found]:::common
    """
    for match in matches:
        original_code = match.strip()
        fixed_code = fix_mermaid(original_code)  # reuse the fixer we wrote earlier

        # Replace only the inner code, keep the ```mermaid fences
        fixed_text = fixed_text.replace(
            f"```mermaid{match}```", f"```mermaid\n{fixed_code}\n```"
        )

    return fixed_text, f"```mermaid\n{fixed_code}\n```"
