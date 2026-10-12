from pathlib import Path

from generate_data import generate


if __name__ == "__main__":
    generate(Path("data/sample/batch_good.jsonl"), rows=10000, bad_rows=False)
    generate(Path("data/sample/batch_bad.jsonl"), rows=1000, bad_rows=True)
    print("Generated reliability demo data:")
    print("- data/sample/batch_good.jsonl: valid load and performance test")
    print("- data/sample/batch_bad.jsonl: duplicates, missing values and negative amounts")
    print("Use the bad batch to demonstrate failure, quarantine and idempotent rerun recovery.")
