import pandas as pd
from src.pipeline import FinancialPipeline
from scripts.generate_chaos import create_chaos_file
from pathlib import Path

INPUT_FILE = Path("data/raw/generated_transactions.csv")
EXPECTED_FILE = Path("data/raw/clean_transactions.csv")
OUTPUT_FILE = Path("data/processed/normalized_data.csv")

def test_pipeline_integration(tmpdir):
    create_chaos_file()
    temp_output_path = Path(tmpdir) / "test_output.csv"
    pipeline = FinancialPipeline(
        input_path=str(INPUT_FILE),
        output_path=str(temp_output_path)
    )
    pipeline.run()

    expected_df = pd.read_csv(EXPECTED_FILE)
    actual_df = pd.read_csv(OUTPUT_FILE)

    assert len(actual_df) == len(expected_df), "Mismatched row count"
    pd.testing.assert_frame_equal(
        actual_df.reset_index(drop=True), 
        expected_df.reset_index(drop=True),
        check_dtype=False
    )
