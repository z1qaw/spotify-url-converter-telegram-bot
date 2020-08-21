import re

def escape_markdown(string: str):
    match_md = r'((([_*]).+?\3[^_*]*)*)([_*])'
    return re.sub(match_md, "\g<1>\\\\\g<4>", string)

def can_value_be_int(value):
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False