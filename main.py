import argparse
from src.pipeline import FinancialPipeline

def main() -> None:
    '''
    CLI entrypoint: parse args and run the FinancialPipeline with provided input/output paths.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", type=str, default="data/raw/generated_transactions.csv", help="Path to input CSV")
    parser.add_argument("--output", type=str, default="data/processed/normalized_data.csv", help="Path to output CSV")

    args = parser.parse_args()

    # Creates output directory and file during pipeline run if none exists
    pipeline = FinancialPipeline(input_path=args.input, output_path=args.output)
    pipeline.run()

if __name__ == "__main__":
    main()
