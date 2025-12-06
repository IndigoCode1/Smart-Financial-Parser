from typing import Optional

CANONICAL_MERCHANTS = None

def parse_merchant(raw_merchant: str) -> str:
    if not raw_merchant:
        return "UNKNOWN"
    
    return raw_merchant