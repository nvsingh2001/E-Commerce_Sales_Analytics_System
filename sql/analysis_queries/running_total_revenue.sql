SELECT
    DATE_TRUNC('month', order_date) AS revenue_month,
    SUM(line_total) AS monthly_revenue,
    SUM(SUM(line_total)) OVER (
        ORDER BY DATE_TRUNC('month', order_date)
    ) AS running_total
FROM fact_orders
WHERE order_status = 'Completed'
GROUP BY revenue_month
ORDER BY revenue_month;