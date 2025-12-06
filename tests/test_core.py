import pytest
from datetime import date
from src.normalization.dates import parse_date
from src.normalization.amounts import parse_amount
from src.normalization.merchants import parse_merchant

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

    def test_fuzzy_match_contains(self):
        assert parse_merchant("AMZN Mktp US") == "AMAZON"

    def test_fuzzy_match_typo_ish(self):
        assert parse_merchant("Uber Technologies") == "UBER"

    def test_unicode_handling(self):
        assert parse_merchant("Starbucks ☕️") == "STARBUCKS"

    def test_unknown_merchant(self):
        assert parse_merchant("Joe's Coffee") == "JOE'S COFFEE"

    def test_empty_returns_unknown(self):
        assert parse_merchant("") == "UNKNOWN"
