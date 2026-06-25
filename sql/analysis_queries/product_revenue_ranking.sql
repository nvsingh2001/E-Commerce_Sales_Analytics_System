SELECT
    dp.product_id,
    dp.product_name,
    SUM(fo.line_total) AS total_revenue,
    RANK() OVER (
        ORDER BY SUM(fo.line_total) DESC
    ) AS revenue_rank
FROM fact_orders fo
JOIN dim_products dp
    ON fo.product_id = dp.product_id
WHERE fo.order_status = 'Completed'
GROUP BY
    dp.product_id,
    dp.product_name;