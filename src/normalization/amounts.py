from typing import Optional
import re

def parse_amount(amount_str: str) -> Optional[float]:
    if not amount_str:
        return None
    
    raw = amount_str.strip()
    is_negative = False

    if raw.startswith('(') and raw.endswith(')'):
        is_negative = True
        raw = raw[1:-1]

    if raw.startswith('-'):
        is_negative = True
        raw = raw[1:]

    cleaned_str = re.sub(r'[$,]|[a-zA-Z]+', '', raw)

    try:
        val = float(cleaned_str.strip())
        if is_negative:
            val = -val
        return val
    except (ValueError, AttributeError):
        return None
    