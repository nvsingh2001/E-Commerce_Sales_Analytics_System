SELECT
    dc.customer_segment,
    ROUND(SUM(fo.line_total) / COUNT(DISTINCT fo.order_id), 2) AS average_order_value
FROM fact_orders fo
JOIN dim_customers dc
    ON fo.customer_id = dc.customer_id
WHERE fo.order_status = 'Completed'
GROUP BY dc.customer_segment
ORDER BY average_order_value DESC;
