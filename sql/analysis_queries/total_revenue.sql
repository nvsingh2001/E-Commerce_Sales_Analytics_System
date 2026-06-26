SELECT SUM(line_total) AS total_revenue
FROM fact_orders
WHERE order_status = 'Completed';
