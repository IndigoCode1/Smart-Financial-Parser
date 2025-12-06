import pandas as pd
from pathlib import Path
import sys

class FinancialPipeline:
    def __init__(self, input_path: str, output_path: str) -> None:
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)

    def load_data(self) -> pd.DataFrame:
        if not self.input_path.exists():
            raise FileNotFoundError(f"Error: Input file not found at {self.input_path}")
        
        print(f"Loading data from {self.input_path}")

        df = pd.read_csv(self.input_path, dtype=str)

        print(f"Loaded {len(df)} rows successfully.")
        return df
    
    def run(self) -> None:
        try:
            df = self.load_data()
        except Exception as e:
            print(f"Critical Error during loading: {e}")
            sys.exit(1)
        
        # Normalization logic not implemented yet

        print("\nRaw Data Preview (First 5 rows):")
        print(df.head())