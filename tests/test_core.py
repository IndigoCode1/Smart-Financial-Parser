import pytest
from datetime import date
from src.normalization.dates import parse_date

def test_iso_format():
    assert parse_date("2025-01-12") == date(2025, 1, 12)

def test_us_short_format():
    assert parse_date("01/01/25") == date(2025, 1, 1)

def test_human_readable():
    assert parse_date("Feb 26, 2025") == date(2025, 2, 26)

def test_dot_format():
    assert parse_date("2025.10.22") == date(2025, 10, 22)

def test_difficult_human_format():
    assert parse_date("Sept. 3rd, 2024") == date(2024, 9, 3)

def test_invalid_date_returns_none():
    assert parse_date("2025/13/01") is None

def test_garbage_string_returns_none():
    assert parse_date("Not a date") is None

def test_empty_string_returns_none():
    assert parse_date("") is None

