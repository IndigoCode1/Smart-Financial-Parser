# Smart Financial Parser: Design & Technical Architecture

## 1. Executive Summary
The Smart Financial Parser is an AI-Native ETL (Extract, Transform, Load) solution designed to ingest, normalize, and categorize messy financial transaction data. Unlike rigid parsers that fail on unexpected formats, this system utilizes a fault-tolerant, heuristic-based pipeline to handle inconsistent dates, noisy merchant names, and non-standard currency formatting.

The design philosophy prioritizes resilience over rigidity. Rather than crashing on malformed inputs, the system attempts to normalize them using fuzzy logic and regex patterns, logging any unrecoverable errors for human review.

---

## 2. Technical Stack
* **Language - Python 3.8+:** The industry standard for data engineering and ETL tasks.
* **Data Processing - Pandas:** Used for high-speed CSV ingestion and data manipulation. While Python's built-in csv module is lighter, I chose pandas for its robust handling of arbitrary column mapping and `NaN` values. There is also possibility of future extensibility for complex analytics with pandas.
* **String Matching - RapidFuzz:** Chosen for merchant normalization. It is faster than `Levenshtein` and allows for partial token matching (e.g., matching "Home Depot" to "The Home Depot").
* **Date Parsing - Dateutil:** Used for its fuzzy date parsing capabilities, handling formats like "Jan 1st 23" that break standard `datetime` libraries.
* **Testing - Pytest:** Chosen over unittest for its concise syntax, powerful fixtures, and detailed failure reporting, which accelerated my TDD cycle.
* **Data Generation - Faker:** Used to generate realistic, seeded synthetic data for deterministic integration testing.

---

## 3. Architecture Overview
The system follows a modular pipeline architecture implemented in src/pipeline.py. The data flows through four distinct stages:

### Stage 1: Ingestion & Mapping
* **String-First Loading:** The pipeline loads all CSV data as strings initially. This prevents pandas from prematurely inferring types (which causes crashes on mixed-type columns) and ensures "strange" inputs are preserved for the normalization logic.
* **Heuristic Column Mapping:** The system dynamically identifies columns. It scans headers for keywords (e.g., "txn", "desc", "cost") to map inputs to the internal schema (date, merchant, amount), making it adaptable to different bank export formats.

### Stage 2: Normalization
Data is passed through specialized processors for each field:

1.  **Date Normalization (`src/normalization/dates.py`)**
    * **Strategy:** Uses `dateutil.parser.parse` with `fuzzy=True`.
    * **Edge Case Handling:** Pre-processes strings using regex to remove ordinal suffixes (e.g., "3rd", "1st") which often confuse standard parsers.
    * **Validation:** Returns `None` if parsing fails, triggering an error log entry.

2.  **Amount Normalization (`src/normalization/amounts.py`)**
    * **Sanitization:** Uses regex to strip currency codes (USD), symbols ($), and whitespace while preserving decimals and negative signs.
    * **Accounting Logic:** Specifically detects accounting negative formats (parentheses). If a value appears as `(500.00)`, the system detects the parenthesis, strips them, and negates the float value to `-500.00`.

3.  **Merchant Normalization (`src/normalization/merchants.py`)**
    * **Noise Removal:** cleans inputs by removing legal entities ("INC", "LLC"), common noise words ("WWW", "USA"), and special characters. The regex used here was AI-assisted but manually verified against test cases involving emojis and symbols.
    * **Ticker Aliasing:** Checks the first word of the merchant string against a ticker map (e.g., "AMZN" → "AMAZON").
    * **Canonical Matching:**
        1.  **O(1) Lookup:** Checks a pre-loaded dictionary of known merchants.
        2.  **Fuzzy Match:** If no exact match is found, uses `rapidfuzz` to find the closest canonical merchant (threshold > 80%).
        3.  **Fallback:** Returns the cleaned string if no match is found.

### Stage 3: Categorization (`src/normalization/categories.py`)
Categorization uses a deterministic "Waterfall" classifier to ensure speed and zero inference costs (avoiding API calls for every row):

1.  **Canonical Map:** If `merchants.py` identified "UBER", it is immediately tagged as **Transport**.
2.  **Keyword Heuristics:** If the merchant is unknown, the system scans the raw name for keywords (e.g., "PLUMBING" maps to **Utilities**).
    * *Design Detail:* Regex word boundaries (`\b`) are used to ensure keywords are distinct words, preventing false positives (e.g., preventing "TITAN" from matching "IT").
3.  **Default:** Transactions that fail both checks are classified as **Miscellaneous** or Local Business.

### Stage 4: Reporting
* **Error Logging:** Rows that fail normalization are **not dropped**. They are written to `errors.log` (in CSV format) with a specific error reason, preserving data integrity and allowing for manual fixing.
* **Quality Report:** A summary text file is generated detailing total spend, the top spending category, and row success rates.

---

## 4. Data Strategy

### Configuration Files
The system relies on external CSV configurations to allow logic updates without code changes:
* **`canonical_merchants.csv`:** Contains the "Golden Source" of truth for merchant names and their default categories.
* **`keywords.csv`:** A fallback list of keywords used when the specific merchant is not recognized.

### Synthetic Data Generation (`scripts/generate_chaos.py`)
To ensure robustness, a "Chaos Generator" was built to create difficult test data.
* **Seeding:** `Faker` and `random` are seeded (Seed: 42) to ensure tests are deterministic.
* **90/10 Logic:** The generator uses 90% "known" merchants (like Starbucks) to test canonical matching, and 10% random "faker" companies to test the `Miscellaneous` fallback logic.
* **Edge Cases:** Specific "hard-coded" edge cases (e.g., "Sept. 3rd", "UBER *TRIP") are injected to verify the normalizers.

---

## 5. Verification & AI Implementation

### Verification Strategy
* **Unit Testing (TDD):** Tests were written before and during development (`test_core.py`).
* **Integration Testing:** The `test_pipeline.py` ensures that running the pipeline on `generated_transactions.csv` always produces the byte-perfect `clean_transactions.csv`.
* **Manual Audit:** Outputs are manually inspected to ensure logic holds up against real-world ambiguity.

### AI Implementation Notes
Please view the README.md for my detailed AI Usage Disclosure