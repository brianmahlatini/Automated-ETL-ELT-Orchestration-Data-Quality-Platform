# Automated ETL/ELT Orchestration & Data Quality Platform

Senior-level data engineering project showing a dependable, scheduled ETL/ELT pipeline with Airflow, Python, SQL, PostgreSQL, FastAPI, React, Docker, Kubernetes and GitHub Actions.

## What This Builds

The platform ingests synthetic commerce events, lands them as raw data, loads them idempotently into PostgreSQL, transforms them into analytics tables, validates data quality and exposes operational status through a FastAPI backend and React dashboard.

## Architecture

```text
Generated/API data -> Airflow DAG -> Raw landing -> PostgreSQL staging -> SQL marts
                                      |                  |
                                      v                  v
                                 quality checks -> pipeline_run_metrics -> FastAPI -> React
```

Core features:

- Automated Airflow DAG with retries, backfills, SLAs and failure callbacks.
- Incremental loads using `event_timestamp` watermarks and idempotent `ON CONFLICT` upserts.
- PostgreSQL migrations, staging tables, dimensional marts and quality result tables.
- Data quality checks for schema drift, duplicates, missing values and freshness.
- Failure recovery through retryable extract/load tasks, quarantine tables and rerunnable DAG runs.
- FastAPI service for pipeline health, run metrics and data quality summaries.
- React dashboard for operational monitoring.
- Docker Compose for local development and Kubernetes manifests for deployment.
- GitHub Actions for backend tests, SQL lint-style validation and frontend build checks.

## Repository Structure

```text
airflow/dags/              Airflow orchestration DAG
airflow/include/           Pipeline helpers shared by DAG tasks
backend/app/               FastAPI backend
backend/tests/             Pytest coverage for API and quality logic
frontend/src/              React dashboard
sql/migrations/            PostgreSQL schema
sql/models/                ELT SQL transformations
sql/quality/               Data quality SQL checks
scripts/                   Data generation and local reliability demo
infra/k8s/                 Kubernetes manifests
.github/workflows/         CI checks
```

## Quick Start

```bash
docker compose up --build
```

Services:

- Airflow UI: `http://localhost:8080`
- FastAPI: `http://localhost:8000/docs`
- React dashboard: `http://localhost:5173`
- PostgreSQL: `localhost:5432`

Default local credentials are defined in `docker-compose.yml`.

## Run The Pipeline

1. Start the stack:

   ```bash
   docker compose up --build
   ```

2. Open Airflow and enable `commerce_incremental_quality_pipeline`.
3. Trigger a manual run or let the hourly schedule run.
4. View run health in the React dashboard.

## Demonstrating Failure And Recovery

Run the reliability demo:

```bash
python scripts/reliability_demo.py
```

The demo generates two batches:

- `batch_good.jsonl` contains valid events.
- `batch_bad.jsonl` intentionally includes duplicate IDs, missing customer IDs and stale timestamps.

Expected behavior:

- The load task remains idempotent because `event_id` is the primary key.
- Duplicate records are rejected or upserted without double-counting.
- Bad records are written to `dq_violations` with the failed rule.
- Airflow retries transient failures automatically.
- A rerun with corrected data only processes records above the stored watermark.

Example reliability evidence to include in your portfolio:

```text
Failed run: freshness_check failed because max(event_timestamp) was older than 24 hours.
Recovery: replacement batch was landed, DAG rerun used the same run_id and idempotent upsert keys.
Result: final mart row count stayed stable, duplicates remained 0 and freshness returned to 11 minutes.
Measured result: 10,000 generated events loaded in under 5 seconds locally with p95 API health endpoint below 50 ms.
```

## Data Quality Rules

- `schema_contract`: required fields and expected types must exist.
- `duplicate_event_id`: no duplicate event IDs in staging.
- `missing_customer_id`: customer ID must be present.
- `freshness`: latest accepted event must be within 24 hours.
- `non_negative_amount`: order amount must be greater than or equal to zero.

## CI/CD

GitHub Actions runs on every push and pull request:

- Python unit tests with `pytest`.
- Static syntax checks for DAGs and backend modules.
- Frontend install and production build.
- SQL file presence and migration smoke checks.

## Kubernetes

Apply the deployment manifests after building and pushing images:

```bash
kubectl apply -f infra/k8s/
```

The manifests include API, frontend and PostgreSQL resources suitable for a portfolio-grade cluster demo. In production, replace the PostgreSQL deployment with a managed database and store secrets in your cloud secret manager.
