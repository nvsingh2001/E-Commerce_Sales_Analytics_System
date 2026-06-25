CREATE OR REPLACE VIEW monthly_revenue_trends AS
SELECT
    dc.country,
    EXTRACT(YEAR FROM fo.order_date) AS year,
    EXTRACT(MONTH FROM fo.order_date) AS month,
    SUM(fo.line_total) AS total_revenue
FROM fact_orders fo
JOIN dim_customers dc
    ON fo.customer_id = dc.customer_id
WHERE fo.order_status = 'Completed'
GROUP BY
    dc.country,
    year,
    month;