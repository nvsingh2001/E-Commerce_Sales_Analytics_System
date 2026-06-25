SELECT
    dc.customer_id,
    dc.country,
    SUM(fo.line_total) AS lifetime_spend
FROM fact_orders fo
JOIN dim_customers dc
    ON fo.customer_id = dc.customer_id
WHERE fo.order_status = 'Completed'
GROUP BY
    dc.customer_id,
    dc.country
ORDER BY lifetime_spend DESC
LIMIT 10;