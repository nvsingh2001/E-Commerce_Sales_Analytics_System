SELECT
    dc.country,
    SUM(fo.line_total) AS total_revenue
FROM fact_orders fo
JOIN dim_customers dc
    ON fo.customer_id = dc.customer_id
WHERE fo.order_status = 'Completed'
GROUP BY dc.country
ORDER BY total_revenue DESC;