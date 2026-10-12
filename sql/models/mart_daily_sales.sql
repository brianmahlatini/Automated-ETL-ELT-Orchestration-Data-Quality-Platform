insert into mart_daily_sales (sales_date, orders, revenue, updated_at)
select
    event_timestamp::date as sales_date,
    count(*) as orders,
    sum(amount) as revenue,
    now() as updated_at
from raw_events
group by event_timestamp::date
on conflict (sales_date)
do update set
    orders = excluded.orders,
    revenue = excluded.revenue,
    updated_at = now();
