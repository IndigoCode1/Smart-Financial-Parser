import csv
import re
from pathlib import Path
from typing import Dict, List, Optional
from rapidfuzz import process, fuzz

BASE_DIR = Path(__file__).resolve().parents[2]
MERCHANT_FILE = BASE_DIR / Path("data/config/canonical_merchants.csv")

# Module-level caches avoid re-reading config on every row
_CANONICAL_NAMES = []
_CATEGORY_MAP = {}
_TICKER_ALIASES = {}

def load_merchant_db():
    '''
    Lazy-load canonical merchant names, categories, and optional ticker aliases from config CSV.
    '''
    if _CANONICAL_NAMES:
        return
    
    if not MERCHANT_FILE.exists():
        print(f"Merchant DB not found at {MERCHANT_FILE}")
        return
    
    try:
        with open(MERCHANT_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['canonical_name'].strip().upper()
                category = row['category'].strip()
                ticker = row.get('ticker','').strip().upper()

                _CANONICAL_NAMES.append(name)
                _CATEGORY_MAP[name] = category
                
                # Only swaps when ticker appears as the first token
                if ticker:
                    _TICKER_ALIASES[ticker] = name
    except Exception as e:
        print(f"Error reading merchant CSV: {e}")
        pass

def clean_merchant_name(raw: str) -> str:
    '''
    Standardize merchant text by removing corporate suffixes/noise and normalizing separators.
    '''
    s = raw.upper().strip()

    for separator in ['*', '.', '_']:
        s = s.replace(separator, ' ')

    common_noise = [r'INC', r'LLC', r'LTD', r'CORP', 
                    r'US', r'USA', r'TECHNOLOGIES', r'NV', r'BV', 
                    r'WWW', r'CO', r'ORG']
    
    for noise_word in common_noise:
        pattern = r'\b' + noise_word + r'\b'
        s = re.sub(pattern, '', s)

    s = re.sub(r'[^A-Z0-9\s]', '', s)

    return " ".join(s.split())

def parse_merchant(raw_merchant: str) -> str:
    '''
    Canonicalize a raw merchant using cleaning, optional ticker alias expansion, exact match, then fuzzy match.
    '''
    if not raw_merchant or not isinstance(raw_merchant, str):
        return "UNKNOWN"
    
    load_merchant_db()

    cleaned_input = clean_merchant_name(raw_merchant)

    if not _CANONICAL_NAMES:
        return cleaned_input
    
    first_word = cleaned_input.split(' ')[0]

    if first_word in _TICKER_ALIASES:
        canonical_name = _TICKER_ALIASES[first_word]
        cleaned_input = cleaned_input.replace(first_word, canonical_name, 1)

    # Exact Match
    if cleaned_input in _CATEGORY_MAP:
        return cleaned_input
    
    # Fuzzy Match
    result = process.extractOne(
        cleaned_input,
        _CANONICAL_NAMES,
        scorer=fuzz.token_set_ratio,
        score_cutoff=80.0
    )

    if result:
        match_name, score, _ = result
        return match_name

    # Return Cleaned Name
    return cleaned_input

def get_category_map() -> Dict[str, str]:
    '''
    Expose canonical merchant-to-category mapping for the category assignment stage.
    '''
    load_merchant_db()
    return _CATEGORY_MAP