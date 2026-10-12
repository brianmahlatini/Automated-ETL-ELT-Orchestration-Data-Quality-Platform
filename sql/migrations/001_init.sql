create table if not exists raw_events (
    event_id text primary key,
    event_timestamp timestamptz not null,
    customer_id text,
    product_id text not null,
    quantity integer not null,
    amount numeric(12, 2) not null,
    source_file text not null,
    ingested_at timestamptz not null default now()
);

create table if not exists dq_results (
    id bigserial primary key,
    rule_name text not null,
    status text not null,
    checked_at timestamptz not null default now(),
    failed_count integer not null,
    details jsonb not null default '{}'::jsonb
);

create table if not exists dq_violations (
    id bigserial primary key,
    event_id text,
    rule_name text not null,
    payload jsonb not null,
    created_at timestamptz not null default now()
);

create table if not exists pipeline_watermarks (
    pipeline_name text primary key,
    last_event_timestamp timestamptz not null,
    updated_at timestamptz not null default now()
);

create table if not exists pipeline_run_metrics (
    run_id text primary key,
    status text not null,
    started_at timestamptz not null default now(),
    finished_at timestamptz,
    rows_loaded integer not null default 0,
    rows_rejected integer not null default 0,
    error_message text
);

create table if not exists mart_daily_sales (
    sales_date date primary key,
    orders integer not null,
    revenue numeric(14, 2) not null,
    updated_at timestamptz not null default now()
);
