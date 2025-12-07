import pytest
from datetime import date
from src.normalization.dates import parse_date
from src.normalization.amounts import parse_amount
from src.normalization.merchants import parse_merchant
from src.normalization.categories import assign_category

class TestDates:
    def test_iso_format(self):
        assert parse_date("2025-01-12") == date(2025, 1, 12)

    def test_us_short_format(self):
        assert parse_date("01/01/25") == date(2025, 1, 1)

    def test_human_readable(self):
        assert parse_date("Feb 26, 2025") == date(2025, 2, 26)

    def reversed_test_human_readable(self):
        assert parse_date("2025 27 feb") == date(2025, 2, 27)

    def test_dot_format(self):
        assert parse_date("2025.10.22") == date(2025, 10, 22)

    def test_human_format(self):
        assert parse_date("Sept. 3rd, 2024") == date(2024, 9, 3)

    def test_difficult_human_format(self):
        assert parse_date("Feb ury 19th, 2024") == date(2024, 2, 19)

    def test_sad_paths(self):
        assert parse_date("2025/13/01") is None
        assert parse_date("Not a date") is None
        assert parse_date("") is None

class TestAmounts:
    def test_clean_currency(self):
        assert parse_amount("$100.00") == 100.0

    def test_comma_separator(self):
        assert parse_amount("1,000.00") == 1000.0

    def test_extra_space(self):
        assert parse_amount("1 000.00") == 1000.0

    def test_currency_text(self):
        assert parse_amount("50.00 USD") == 50.0
        assert parse_amount("USD 50.00") == 50.0

    def test_negatives(self):
        assert parse_amount("(500.00)") == -500.0
        assert parse_amount("-500.00") == -500.0

    def test_sad_paths(self):
        assert parse_amount("Free") is None
        assert parse_amount("N/A") is None
        assert parse_amount("") is None

class TestMerchants:
    def test_basic_cleaning(self):
        assert parse_merchant("  uber   ") == "UBER"

    def test_exact_match(self):
        assert parse_merchant("AMAZON") == "AMAZON"

    def test_fuzzy_match_start(self):
        assert parse_merchant("UBER *TRIP") == "UBER"

    def test_fuzzy_match_long(self):
        assert parse_merchant("Uber Technologies") == "UBER"

    def test_fuzzy_match_short(self):
        assert parse_merchant("UBER EATS") == "UBER"

    def test_fuzzy_match_contains(self):
        assert parse_merchant("AMZN Mktp US") == "AMAZON"

    def test_fuzzy_match_typo_ish(self):
        assert parse_merchant("Uber Technologies") == "UBER"

    def test_unicode_handling(self):
        assert parse_merchant("Starbucks ☕️") == "STARBUCKS"

    def test_unknown_merchant(self):
        assert parse_merchant("Joe's Coffee") == "JOES COFFEE"

    def test_empty_returns_unknown(self):
        assert parse_merchant("") == "UNKNOWN"

    def test_ticker_swap_basic(self):
        assert parse_merchant("WMT SUPERCENTER") == "WALMART"

    def test_ticker_swap_standalone(self):
        assert parse_merchant("AMZN") == "AMAZON"

    def test_multi_alias_support(self):
        assert parse_merchant("AWS WEB SVS") == "AWS"

    def test_ticker_embedded_in_word(self):
        assert parse_merchant("TGIF DINING") != "TARGET"

    def test_similar_but_distinct_brands(self):
        home = parse_merchant("HOME DEPOT")
        office = parse_merchant("OFFICE DEPOT")
        assert home != office

    def test_short_names(self):
        assert parse_merchant("BP GAS") == "BP"

    def test_domain_names(self):
        assert parse_merchant("WWW.AMAZON.COM") == "AMAZON"
        assert parse_merchant("NETFLIX.COM") == "NETFLIX"

    def test_hyphenated_brands(self):
        assert parse_merchant("CHICK-FIL-A") == "CHICK-FIL-A"

class TestCategories:
    def test_fallback_dining_keyword(self):
        assert assign_category("LOCAL COFFEE HOUSE") == "Dining"

    def test_fallback_groceries_keyword(self):
        assert assign_category("SARAH'S DELI AND SANDWICHES") == "Groceries"
    
    def test_fallback_gas_keyword(self):
        assert assign_category("PETRO FUEL STOP") == "Gas"

    def test_fallback_transport_keyword(self):
        assert assign_category("JOE'S AUTOMOTIVE REPAIR") == "Transport"
    
    def test_fallback_shopping_keyword(self):
        assert assign_category("VINTAGE CLOTHING BOUTIQUE") == "Shopping"
        
    def test_fallback_entertainment_keyword(self):
        assert assign_category("MAIN STREET THEATRE") == "Entertainment"

    def test_fallback_tech_keyword(self):
        assert assign_category("CREATIVE DIGITAL MARKETING") == "Tech"
    
    def test_fallback_utilities_keyword(self):
        assert assign_category("ACE PLUMBING SERVICES") == "Utilities"

    def test_fallback_insurance_keyword(self):
        assert assign_category("TRUSTED LIFE INSURANCE") == "Insurance"

    def test_fallback_health_keyword(self):
        assert assign_category("BRIGHT EYES OPTICAL") == "Health"
    
    def test_fallback_telecom_keyword(self):
        assert assign_category("GIGABIT BROADBAND LLC") == "Telecom"

    def test_fallback_finance_keyword(self):
        assert assign_category("QUICK CASH LOAN COMPANY") == "Finance"

    def test_fallback_education_keyword(self):
        assert assign_category("TUTORING ACADEMY") == "Education"
    
    def test_no_match_fallback(self):
        assert assign_category("GENERAL MERCHANDISE WAREHOUSE") == "Miscellaneous" 

    def test_canonical_dining_priority(self):
        assert assign_category("STARBUCKS") == "Dining"

    def test_canonical_transport_priority(self):
        assert assign_category("UBER") == "Transport"
        
    def test_canonical_finance_priority(self):
        assert assign_category("CHASE") == "Finance"

    def test_canonical_unconventional_category(self):
        assert assign_category("AMAZON") == "Shopping"