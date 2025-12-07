import pandas as pd
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

from src.normalization.dates import parse_date
from src.normalization.amounts import parse_amount
from src.normalization.merchants import parse_merchant
from src.normalization.categories import assign_category

class FinancialPipeline:
    def __init__(self, input_path: str, output_path: str) -> None:
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.report_path = self.output_path.parent / "data_quality_report.txt"
        self.error_path = self.output_path.parent / "errors.log"

        self.stats = {
            "total_rows": 0,
            "success_rows": 0,
            "failed_rows": 0,
            "top_category": "N/A",
            "total_spend": 0.0
        }

    def load_data(self) -> pd.DataFrame:
        if not self.input_path.exists():
            raise FileNotFoundError(f"Error: Input file not found at {self.input_path}")
        
        print(f"Loading data from {self.input_path}")
        df = pd.read_csv(self.input_path, dtype=str)
        df = df.fillna("")

        return df
    
    def map_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        cols = [c.lower() for c in df.columns]
        mapping = {}

        date_candidates = ['date', 'time', 'txn', 'timestamp', 'day']
        for col in df.columns:
            if any(candidate in col.lower() for candidate in date_candidates):
                mapping['date'] = col
                break

        merchant_candidates = ['merchant', 'desc', 'vendor', 'payee']
        for col in df.columns:
            if any(candidate in col.lower() for candidate in merchant_candidates):
                mapping['merchant'] = col
                break

        amount_candidates = ['amount', 'amt', 'value', 'cost', 'total', 'price']
        for col in df.columns:
            if any(candidate in col.lower() for candidate in amount_candidates):
                mapping['amount'] = col
                break

        missing = [key for key in ['date', 'merchant', 'amount'] if key not in mapping]
        if missing:
            raise ValueError(f"Could not automatically identify columns for: {', '.join(missing)}")

        print(f"Column Mapping Found: {mapping}")
        return mapping

    def process_row(self, row:pd.Series, mapping: Dict[str, str]) -> Tuple[Optional[Dict], Optional[Dict]]:
        raw_date = row[mapping['date']]
        raw_merc = row[mapping['merchant']]
        raw_amt = row[mapping['amount']]

        clean_date = parse_date(raw_date)
        if not clean_date:
            error_row = row.to_dict()
            error_row['Error_Reason'] = f"Invalid Date Format: '{raw_date}'"
            return None, error_row
        
        clean_amount = parse_amount(raw_amt)
        if clean_amount is None:
            error_row = row.to_dict()
            error_row['Error_Reason'] = f"Invalid Amount Format: '{raw_amt}'"
            return None, error_row
        
        clean_merchant = parse_merchant(raw_merc)

        category = assign_category(clean_merchant)

        success = {
            "Date": clean_date.isoformat(),
            "Merchant": clean_merchant,
            "Amount": clean_amount,
            "Category": category,
            "Original_Desc": raw_merc 
        }

        return success, None
        
    def generate_report(self, df: pd.DataFrame) -> None:
        if not df.empty:
            category_spend = df.groupby("Category")["Amount"].sum()
            if not category_spend.empty:
                top_category = category_spend.idxmax()
                top_val = category_spend.max()
                self.stats["top_category"] = f"{top_category} (${top_val:,.2f})"
                self.stats["total_spend"] = df["Amount"].sum()

        report_content = (
            f"FINANCIAL DATA REPORT\n"
            f"================================\n"
            f"Input File: {self.input_path.name}\n"
            f"Total Rows:   {self.stats['total_rows']}\n"
            f"Successfully Parsed: {self.stats['success_rows']}\n"
            f"Failed / Skipped: {self.stats['failed_rows']}\n"
            f"--------------------------------\n"
            f"Total Spend: ${self.stats['total_spend']:,.2f}\n"
            f"Top Category: {self.stats['top_category']}\n"
            f"Clean Data: {self.output_path}\n"
            f"Error Log: {self.error_path}\n"
        )

        with open(self.report_path, "w", encoding='utf-8') as f:
            f.write(report_content)

        print("\n" + report_content)
        print(f"Report saved to {self.report_path}")

    def run(self) -> None:
        print("Starting Financial Parser")

        try:
            raw_df = self.load_data()
            self.stats["total_rows"] = len(raw_df)
            col_map = self.map_columns(raw_df)
        except Exception as e:
            print(f"Critical Error during loading and setup: {e}")
            sys.exit(1)
        
        clean_rows = []
        error_rows = []
        print("Normalizing data")

        for _, row in raw_df.iterrows():
            success_data, error_data = self.process_row(row, col_map)
            if success_data:
                clean_rows.append(success_data)
                self.stats["success_rows"] += 1
            elif error_data:
                error_rows.append(error_data)
                self.stats["failed_rows"] += 1
        
        clean_df = pd.DataFrame(clean_rows)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_csv(self.output_path, index=False)
        print(f"Clean data saved to {self.output_path}")

        if error_rows:
            error_df = pd.DataFrame(error_rows)
            error_df.to_csv(self.error_path, index=False)
            print(f"{len(error_rows)} errors logged to {self.error_path}")
        else:
            print("No errors found!")

        self.generate_report(clean_df)