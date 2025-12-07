# Smart Financial Parser

**A robust, fault-tolerant ETL pipeline designed to normalize messy, unstructured financial transaction data into clean data with analytical insights.**

---

## Project Overview
Financial data is rarely clean. It comes with inconsistent dates, messy merchant names (e.g., "UBER *TRIP"), and weird currency formats (e.g., "(500.00)"). This tool is an AI-Native Engineering solution that ingests raw CSVs, normalizes the data using a multi-stage heuristic pipeline, and categorizes spending with high precision.

### Key Features
* **Resilient Ingestion:** Handles arbitrary column names and fills missing values to prevent pipeline crashes.
* **Smart Normalization:**
    * **Dates:** Parses ambiguous formats ("Sept. 3rd", "2025.01.01") using fuzzy logic.
    * **Amounts:** Handles accounting negatives (parentheses) and currency noise.
    * **Merchants:** Uses fuzzy matching (`rapidfuzz`) and ticker aliases to canonicalize vendors (e.g., "AMZN Mktp" to "AMAZON").
* **Error Logging:** Faulty rows are not dropped; they are logged to `errors.log` for human review.
* **Deterministic Testing:** All synthetic data and unit tests are seeded for reproducibility.

### Supported Categories
The parser automatically classifies transactions into the following categories based on canonical mapping and keyword heuristics:

* **Groceries** (e.g., Whole Foods, Kroger, Safeway)
* **Dining** (e.g., Starbucks, McDonald's, Local Cafes)
* **Gas** (e.g., Shell, Chevron, Wawa)
* **Transport** (e.g., Uber, Lyft, Airlines, Public Transit)
* **Shopping** (e.g., Amazon, Target, Clothing Stores)
* **Entertainment** (e.g., Netflix, Spotify, Cinemas)
* **Tech** (e.g., Apple, AWS, Digital Ocean)
* **Utilities** (e.g., Electric, Water, Waste, Plumbing)
* **Insurance** (e.g., State Farm, Geico)
* **Health** (e.g., Pharmacy, Doctors, Dentists)
* **Telecom** (e.g., Verizon, AT&T, Internet Services)
* **Finance** (e.g., Bank Fees, ATM Withdrawals, Loans)
* **Education** (e.g., Tuition, Books, Courses)

Any transaction that does not match these categories falls back to **Miscellaneous**.

---

## Methodology
### 1. Tools & Technology Stack
I prioritized tools that offered the highest leverage for parsing and matching without reinventing the wheel.

* **Pandas:** Used for high-speed CSV ingestion and data manipulation. While Python's built-in csv module is lighter, I chose pandas for its robust handling of arbitrary column mapping and `NaN` values. There is also possibility of future extensibility for complex analytics with pandas.
* **RapidFuzz:** Chosen for merchant normalization. It is faster than `Levenshtein` and allows for partial token matching (e.g., matching "Home Depot" to "The Home Depot").
* **Dateutil:** Used for its fuzzy date parsing capabilities, handling formats like "Jan 1st 23" that break standard `datetime` libraries.
* **Generative AI:** (See AI Disclosure below) Used to accelerate regex generation, generate datasets, create test cases, fix small bugs, and helped write this README.md in Markdown from my dev notes.
* **Pytest:** Chosen over unittest for its concise syntax, powerful fixtures, and detailed failure reporting, which accelerated my TDD cycle.

### 2. Verification Strategy
To ensure engineering integrity, I implemented a three-tier verification process:

* **Tier 1: Unit Testing (TDD):** I wrote unit tests before and during logic implementation. These tests verify specific edge cases, such as:
    * **Amounts:** Ensuring `(500.00)` converts to `-500.00`.
    * **Merchants:** Ensuring `SHELL*OIL` separates into `SHELL OIL` to match the canonical `SHELL`.
    * **Dates:** Ensuring `Sept. 3rd` strips the suffix before parsing.
* **Tier 2: The Integration Test:** I generated a deterministic dataset (`generated_transactions.csv`) and manually verified the output (`clean_transactions.csv`). The integration test runs the full pipeline and asserts that the output matches the clean file byte-for-byte to prevent regressions.
* **Tier 3: Manual Audit:** I manually inspected the `errors.csv` and the final report to ensure no valid data was being silently discarded.

### 3. Design Decisions
* **The "Waterfall" Categorization:** I avoided using a "black box" AI API for categorization to ensure speed and zero cost. Instead, I built a deterministic classifier:
    1.  **Canonical Match:** If `UBER` is identified, it is immediately tagged `Transport`.
    2.  **Keyword Heuristics:** If the merchant is unknown (e.g., `JOE'S PLUMBING`), the system scans for keywords (`PLUMBING`) to assign `Utilities`.
    3.  **Default:** Falls back to `Miscellaneous`.
* **Pipeline Architecture:** I chose a class-based `FinancialPipeline` structure rather than a script. This allows the logic to be imported and tested in isolation, or easily extended into a web API in the future.

---

## AI Usage Disclosure

In compliance with the hackathon rules, I declare the use of the following AI tools. I maintained full ownership of the code by manually verifying every AI suggestion.

* **Gemini:** Script scaffolding & Regex generation. I manually reviewed the 90/10 split in `generate_chaos.py` and fixed a syntax error in string concatenation that the AI missed.
* **Gemini:** Unit Test generation. To validate, I read through every generated test case to ensure it actually tested the edge case described. 
* **Gemini:** Helped me write this README.md file. I kept a log of my developer notes, and had it come up with the Markdown syntax and help clean up my log. I manually read through and typed everything I wanted into this README.md.
* **Gemini:** Bug fixes. When I came accross a bug I could not fix quickly, I had the AI help me fix it. I manually looked through the code and ran the tests to ensure that the bug was fixed and no new bugs/security issues were caused.
* **ChatGPT / Grok:** Data Generation (Canonical Merchants, Tickers, and Categories). Proprietary or good open source merchant category lists are hard to find. I used AI to generate a baseline CSV for merchants and categories, then manually verified the merchants and categories. I also added and removed ticker symbols and aliases.

---

## Setup & Usage

### 1. Installation
Ensure you have Python 3.8+ installed.
```bash
pip install -r requirements.txt
```
### 2. Generate Test Data
Generate a fresh batch of "messy" data seeded for consistency.
```bash
python scripts/generate_chaos.py
```
### 3. Run the Pipeline
You can run the pipeline using the default chaos data, or specify your own input/output paths via CLI arguments.
* **Default Run:**
```bash
python main.py
```
* **Custom Input/Output:**
```bash
python main.py --input path/to/input.csv --output path/to/output.csv
```
* **Default Input:** data/raw/generated_transactions.csv
* **Default Output:** data/processed/normalized_data.csv
* **Default Report Location:** data/processed/data_quality_report.txt

---

## Running Tests
I prioritized Test-Driven Development (TDD) to ensure robustness. To run the tests, run:
```bash
pytest
```
* **Status:** 51/51 Tests Passed
* **Coverage:** Dates, Amounts, Merchants, Categories, and End-to-End Pipeline.