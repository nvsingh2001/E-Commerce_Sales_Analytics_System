SELECT
    dc.country,
    SUM(fo.revenue) AS total_revenue
FROM fact_orders fo
JOIN dim_customers dc
    ON fo.customer_key = dc.customer_key
GROUP BY dc.country
ORDER BY total_revenue DESC;