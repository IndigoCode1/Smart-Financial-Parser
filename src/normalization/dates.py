from datetime import date
from typing import Optional
import re
from dateutil import parser

def parse_date(date_str: str) -> Optional[date]:
    if not date_str:
        return None
    
    # Straightforward Parsing
    try:
        dt = parser.parse(date_str, fuzzy=True, dayfirst=False)
        return dt.date()
    except (ValueError, TypeError, OverflowError):
        pass

    # Handle any letters that parser doesn't like
    try:
        cleaned_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str, flags=re.IGNORECASE)
        dt = dt = parser.parse(cleaned_str, fuzzy=True, dayfirst=False)
        return dt.date()
    except (ValueError, TypeError, OverflowError):
        pass

    return None
