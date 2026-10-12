from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task

from include.pipeline_tasks import generate_batch, load_incremental, run_sql_file


def notify_failure(context):
    dag_run = context.get("dag_run")
    task_instance = context.get("task_instance")
    print(
        f"ALERT pipeline failure dag_run={dag_run.run_id if dag_run else 'unknown'} "
        f"task={task_instance.task_id if task_instance else 'unknown'}"
    )


@dag(
    dag_id="commerce_incremental_quality_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=True,
    max_active_runs=1,
    default_args={
        "owner": "data-engineering",
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
        "execution_timeout": timedelta(minutes=10),
        "on_failure_callback": notify_failure,
    },
    tags=["etl", "quality", "incremental"],
)
def commerce_pipeline():
    @task
    def extract(run_id: str) -> str:
        return generate_batch(run_id=run_id)

    @task
    def load(path: str, run_id: str) -> dict:
        return load_incremental(path=path, run_id=run_id)

    @task
    def transform() -> None:
        run_sql_file("/opt/airflow/sql/models/mart_daily_sales.sql")

    @task
    def validate() -> None:
        run_sql_file("/opt/airflow/sql/quality/checks.sql")

    batch_path = extract("{{ run_id }}")
    load(batch_path, "{{ run_id }}") >> transform() >> validate()


commerce_pipeline()
