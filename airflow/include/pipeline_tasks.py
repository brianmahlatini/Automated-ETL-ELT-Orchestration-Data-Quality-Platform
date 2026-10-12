import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg

DATABASE_URL = os.getenv("PIPELINE_DATABASE_URL", "postgresql://etl:etl@localhost:5432/lakehouse")
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR", "data/raw"))


def generate_batch(run_id: str, records: int = 500) -> str:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DATA_DIR / f"{run_id}.jsonl"
    now = datetime.now(timezone.utc)
    with path.open("w", encoding="utf-8") as handle:
        for index in range(records):
            payload = {
                "event_id": f"{run_id}-{index}",
                "event_timestamp": now.isoformat(),
                "customer_id": f"customer-{index % 97}",
                "product_id": f"sku-{index % 31}",
                "quantity": (index % 4) + 1,
                "amount": round(((index % 19) + 1) * 7.35, 2),
            }
            handle.write(json.dumps(payload) + "\n")
    return str(path)


def load_incremental(path: str, run_id: str) -> dict:
    loaded = 0
    rejected = 0
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(
            """
            insert into pipeline_run_metrics (run_id, status)
            values (%s, 'running')
            on conflict (run_id) do update set status = 'running', error_message = null
            """,
            (run_id,),
        )
        watermark = conn.execute(
            "select last_event_timestamp from pipeline_watermarks where pipeline_name = 'commerce_events'"
        ).fetchone()
        last_timestamp = watermark[0] if watermark else datetime.min.replace(tzinfo=timezone.utc)
        max_timestamp = last_timestamp

        with Path(path).open(encoding="utf-8") as handle:
            for line in handle:
                event = json.loads(line)
                event_timestamp = datetime.fromisoformat(event["event_timestamp"])
                if event_timestamp <= last_timestamp:
                    continue
                if not event.get("customer_id") or event["amount"] < 0:
                    rejected += 1
                    conn.execute(
                        "insert into dq_violations (event_id, rule_name, payload) values (%s, %s, %s)",
                        (event.get("event_id"), "record_contract", json.dumps(event)),
                    )
                    continue
                conn.execute(
                    """
                    insert into raw_events
                        (event_id, event_timestamp, customer_id, product_id, quantity, amount, source_file)
                    values (%(event_id)s, %(event_timestamp)s, %(customer_id)s, %(product_id)s, %(quantity)s, %(amount)s, %(source_file)s)
                    on conflict (event_id) do update set
                        event_timestamp = excluded.event_timestamp,
                        customer_id = excluded.customer_id,
                        product_id = excluded.product_id,
                        quantity = excluded.quantity,
                        amount = excluded.amount,
                        source_file = excluded.source_file
                    """,
                    {**event, "source_file": Path(path).name},
                )
                loaded += 1
                max_timestamp = max(max_timestamp, event_timestamp)

        conn.execute(
            """
            insert into pipeline_watermarks (pipeline_name, last_event_timestamp)
            values ('commerce_events', %s)
            on conflict (pipeline_name) do update set
                last_event_timestamp = excluded.last_event_timestamp,
                updated_at = now()
            """,
            (max_timestamp,),
        )
        conn.execute(
            """
            update pipeline_run_metrics
            set status = 'success', finished_at = now(), rows_loaded = %s, rows_rejected = %s
            where run_id = %s
            """,
            (loaded, rejected, run_id),
        )
    return {"loaded": loaded, "rejected": rejected}


def run_sql_file(sql_path: str) -> None:
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(Path(sql_path).read_text(encoding="utf-8"))
