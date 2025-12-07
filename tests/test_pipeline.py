import pandas as pd
from src.pipeline import FinancialPipeline
from pathlib import Path
from shutil import copyfile

INPUT_FILE = Path("data/raw/generated_transactions.csv")
EXPECTED_FILE = Path("data/raw/clean_transactions.csv")

def test_pipeline_integration(tmpdir):
    temp_input_path = Path(tmpdir) / "test_input.csv"
    temp_output_path = Path(tmpdir) / "test_output.csv"

    copyfile(INPUT_FILE, temp_input_path)

    pipeline = FinancialPipeline(
        input_path=str(temp_input_path),
        output_path=str(temp_output_path)
    )
    pipeline.run()

    expected_df = pd.read_csv(EXPECTED_FILE)
    actual_df = pd.read_csv(temp_output_path)

    assert len(actual_df) == len(expected_df), "Mismatched row count"
    pd.testing.assert_frame_equal(
        actual_df.reset_index(drop=True), 
        expected_df.reset_index(drop=True),
        check_dtype=False
    )
