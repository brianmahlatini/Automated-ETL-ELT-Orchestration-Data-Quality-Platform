from fastapi import FastAPI

from app.db import get_connection

app = FastAPI(title="ETL/ELT Reliability API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "etl-quality-api"}


@app.get("/pipeline/runs")
def pipeline_runs(limit: int = 20):
    query = """
        select run_id, status, started_at, finished_at, rows_loaded, rows_rejected, error_message
        from pipeline_run_metrics
        order by started_at desc
        limit %s
    """
    with get_connection() as conn:
        return conn.execute(query, (limit,)).fetchall()


@app.get("/quality/summary")
def quality_summary():
    query = """
        select rule_name, status, checked_at, failed_count, details
        from dq_results
        order by checked_at desc
        limit 50
    """
    with get_connection() as conn:
        return conn.execute(query).fetchall()


@app.get("/metrics/reliability")
def reliability_metrics():
    query = """
        select
            count(*) filter (where status = 'success') as successful_runs,
            count(*) filter (where status = 'failed') as failed_runs,
            coalesce(sum(rows_loaded), 0) as rows_loaded,
            coalesce(sum(rows_rejected), 0) as rows_rejected
        from pipeline_run_metrics
    """
    with get_connection() as conn:
        row = conn.execute(query).fetchone()
    total = row["successful_runs"] + row["failed_runs"]
    row["success_rate"] = round(row["successful_runs"] / total, 4) if total else 0
    return row
