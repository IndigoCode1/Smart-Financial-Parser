import csv
from pathlib import Path
from typing import Dict, List, Optional
from src.normalization.merchants import get_category_map
import re

BASE_DIR = Path(__file__).resolve().parents[2]
KEYWORDS_FILE = BASE_DIR / Path("data/config/keywords.csv")
DEFAULT_CATEGORY = "Miscellaneous"

_KEYWORD_RULES = {}

def load_keywords():
    if _KEYWORD_RULES:
        return
    
    if not KEYWORDS_FILE.exists():
        print(f"Warning: Keywords config not found at {KEYWORDS_FILE}")
        return
    
    try:
        with open(KEYWORDS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = row['category'].strip()
                raw_keywords = row['keywords'].upper()

                for keyword in raw_keywords.split('/'):
                    keyword = keyword.strip()
                    if keyword:
                        _KEYWORD_RULES[keyword] = category
    except Exception as e:
        print(f"Error reading keywords CSV: {e}")

def assign_category(merchant_name: str) -> str:
    if not merchant_name:
        return DEFAULT_CATEGORY
    
    load_keywords()
    clean_name = merchant_name.upper().strip()
    canonical_map = get_category_map()

    if clean_name in canonical_map:
        return canonical_map[clean_name]
    
    for keyword, category in _KEYWORD_RULES.items():
        if keyword in clean_name:
            pattern = r'\b' + re.escape(keyword) + r'\b'

            if re.search(pattern, clean_name):
                return category
        
    return DEFAULT_CATEGORY


