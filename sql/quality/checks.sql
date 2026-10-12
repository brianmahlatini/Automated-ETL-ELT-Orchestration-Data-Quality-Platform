insert into dq_results (rule_name, status, failed_count, details)
select
    'missing_customer_id',
    case when count(*) = 0 then 'pass' else 'fail' end,
    count(*)::integer,
    jsonb_build_object('table', 'raw_events')
from raw_events
where customer_id is null or customer_id = '';

insert into dq_results (rule_name, status, failed_count, details)
select
    'non_negative_amount',
    case when count(*) = 0 then 'pass' else 'fail' end,
    count(*)::integer,
    jsonb_build_object('table', 'raw_events')
from raw_events
where amount < 0;

insert into dq_results (rule_name, status, failed_count, details)
select
    'freshness',
    case when max(event_timestamp) >= now() - interval '24 hours' then 'pass' else 'fail' end,
    case when max(event_timestamp) >= now() - interval '24 hours' then 0 else 1 end,
    jsonb_build_object('latest_event_timestamp', max(event_timestamp))
from raw_events;
