# Automated ETL/ELT Orchestration & Data Quality Platform

## Project Overview

This project builds a dependable data pipeline that runs automatically, validates its output and can recover from failed runs. It uses generated commerce event data to demonstrate ingestion, orchestration, incremental loading, SQL transformations, data quality checks, monitoring and deployment readiness.

The pipeline ingests event data, loads it into PostgreSQL, transforms it into analytics tables, checks data quality and exposes pipeline health through a FastAPI backend and React dashboard.

## Tech Stack

| Area | Technology |
| --- | --- |
| Orchestration | Apache Airflow |
| Backend | Python, FastAPI |
| Frontend | React, Vite |
| Database | PostgreSQL |
| Transformations | SQL |
| Data Quality | SQL checks, Python validation |
| Containerisation | Docker, Docker Compose |
| Deployment | Kubernetes manifests |
| CI/CD | GitHub Actions |
| Source Control | Git, GitHub |
| Cloud-ready Storage | AWS S3-ready landing design |

## Project Requirements And Implementation

### 1. Ingest Data From An API Or Files Into PostgreSQL Or S3

The project generates synthetic commerce event data as JSONL files. Airflow ingests these files and loads valid records into PostgreSQL.

Implemented in:

- `scripts/generate_data.py`
- `scripts/reliability_demo.py`
- `airflow/include/pipeline_tasks.py`
- `sql/migrations/001_init.sql`

### 2. Orchestrate Dependencies And Schedules With Airflow DAGs

The Airflow DAG runs on an hourly schedule and controls the full dependency chain:

```text
extract -> load -> transform -> validate
```

Implemented in:

- `airflow/dags/commerce_pipeline.py`

Airflow features used:

- Scheduled runs
- Catchup/backfills
- Retries
- Failure callback alerting
- Task dependencies
- Execution timeout protection

### 3. Use Python And SQL For Transformations

Python is used for ingestion, validation and loading. SQL is used for analytics transformations and quality checks.

Implemented in:

- `airflow/include/pipeline_tasks.py`
- `sql/models/mart_daily_sales.sql`
- `sql/quality/checks.sql`

### 4. Implement Incremental Loads And Idempotent Reruns

The pipeline stores a watermark in PostgreSQL and only processes records newer than the latest loaded `event_timestamp`.

Idempotency is handled with:

- `event_id` as the primary key
- PostgreSQL `ON CONFLICT` upserts
- Pipeline watermarks
- Repeatable Airflow reruns

Implemented in:

- `pipeline_watermarks` table
- `raw_events` table
- `load_incremental()` in `airflow/include/pipeline_tasks.py`

### 5. Add Retries, Backfills, Logging, Alerts And Failure Recovery

The DAG includes:

- `retries=3`
- `retry_delay=2 minutes`
- `catchup=True`
- `on_failure_callback`
- Pipeline run metrics
- Rejected record quarantine

Failed or invalid records are stored in `dq_violations`, while run outcomes are tracked in `pipeline_run_metrics`.

### 6. Test Schema Changes, Duplicates, Missing Values And Data Freshness

Data quality checks include:

- Missing customer IDs
- Negative order amounts
- Freshness checks
- Duplicate protection through primary keys
- Rejected record capture

Implemented in:

- `sql/quality/checks.sql`
- `dq_results`
- `dq_violations`
- `backend/tests/test_api.py`

### 7. Containerise The Environment With Docker

The full local environment runs with Docker Compose.

Services:

- PostgreSQL
- Airflow
- FastAPI backend
- React frontend

Run locally:

```bash
docker compose up --build
```

### 8. Use GitHub Actions For Automated Tests And CI/CD Checks

GitHub Actions runs automated checks on push and pull request.

CI checks:

- Install backend dependencies
- Run Python tests
- Compile backend and DAG Python files
- Install frontend dependencies
- Build React frontend

Implemented in:

- `.github/workflows/ci.yml`

## Senior-Level Evidence

This project demonstrates senior-level engineering through:

- Incremental loading with database watermarks.
- Idempotent reruns using primary keys and upserts.
- Quarantine handling for invalid records.
- Airflow retries and failure callbacks.
- Separate raw, quality, metrics and mart tables.
- A monitoring API for operational visibility.
- A frontend reliability dashboard.
- Docker-based local reproducibility.
- Kubernetes deployment manifests.
- CI checks for backend, DAG and frontend changes.

To demonstrate a failed run, generate a bad batch:

```bash
python scripts/reliability_demo.py
```

The bad batch includes duplicate event IDs, missing customer IDs and invalid negative amounts. The pipeline records rejected rows in `dq_violations`, writes rule outcomes to `dq_results` and keeps successful loads idempotent through `event_id` upserts.

## Architecture

```text
Generated JSONL data
        |
        v
Apache Airflow DAG
        |
        v
PostgreSQL raw_events
        |
        v
SQL transformation marts
        |
        v
Data quality checks
        |
        v
FastAPI metrics API
        |
        v
React reliability dashboard
```

## Repository Structure

```text
airflow/dags/              Airflow orchestration DAG
airflow/include/           Pipeline helpers shared by DAG tasks
backend/app/               FastAPI backend
backend/tests/             Pytest backend tests
frontend/src/              React dashboard
sql/migrations/            PostgreSQL schema
sql/models/                SQL transformations
sql/quality/               Data quality checks
scripts/                   Data generation and reliability demo
infra/k8s/                 Kubernetes manifests
.github/workflows/         CI pipeline
```

## Quick Start

```bash
docker compose up --build
```

Local services:

- Airflow UI: `http://localhost:8080`
- FastAPI docs: `http://localhost:8000/docs`
- React dashboard: `http://localhost:5173`
- PostgreSQL: `localhost:5432`

## Run The Pipeline

1. Start the stack:

   ```bash
   docker compose up --build
   ```

2. Open the Airflow UI.
3. Enable `commerce_incremental_quality_pipeline`.
4. Trigger a manual run or wait for the hourly schedule.
5. Check quality and reliability metrics in the React dashboard.

## Kubernetes

Kubernetes manifests are included for deployment readiness.

```bash
kubectl apply -f infra/k8s/
```

For production, replace the demo PostgreSQL deployment with a managed database and store credentials in a cloud secret manager.
