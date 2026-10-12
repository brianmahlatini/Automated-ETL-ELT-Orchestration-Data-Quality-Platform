import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate(path: Path, rows: int, bad_rows: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    with path.open("w", encoding="utf-8") as handle:
        for index in range(rows):
            event = {
                "event_id": f"event-{index if not bad_rows else index // 2}",
                "event_timestamp": (now - timedelta(minutes=index % 60)).isoformat(),
                "customer_id": f"customer-{index % 100}",
                "product_id": f"sku-{index % 25}",
                "quantity": (index % 5) + 1,
                "amount": round(10 + (index % 100) * 1.15, 2),
            }
            if bad_rows and index % 17 == 0:
                event["customer_id"] = None
            if bad_rows and index % 29 == 0:
                event["amount"] = -5
            handle.write(json.dumps(event) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="data/sample/batch_good.jsonl")
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--bad-rows", action="store_true")
    args = parser.parse_args()
    generate(Path(args.path), args.rows, args.bad_rows)
