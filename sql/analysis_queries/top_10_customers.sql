SELECT
    dc.customer_id,
    dc.country,
    SUM(fo.revenue) AS lifetime_spend
FROM fact_orders fo
JOIN dim_customers dc
    ON fo.customer_key = dc.customer_key
GROUP BY
    dc.customer_id,
    dc.country
ORDER BY lifetime_spend DESC
LIMIT 10;