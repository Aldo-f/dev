import re

def parse_validation_section(md: str) -> list[dict]:
    """Extract a list of validation items from a markdown string.
    Supports lines like:
        - [ ] Do something
        - [x] Done thing
        1. [ ] Item
        * [ ] Item
    Returns a list of dicts: {'raw': line, 'checked': bool, 'text': str}
    """
    validation = []
    in_section = False
    for line in md.splitlines():
        if re.match(r"^#{1,6}\\s+VALIDATION", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            # stop on next heading or empty line after a heading
            if re.match(r"^#", line):
                break
            m = re.search(r"\\[([ xX])\\]", line)
            if m:
                checked = m.group(1).lower() == 'x'
                # strip leading list markers and the checkbox
                text = re.sub(r"^\\s*[-*\\d.*]+\\s*\\[[ xX]\\]\\s*", "", line).strip()
                validation.append({'raw': line, 'checked': checked, 'text': text})
    return validation