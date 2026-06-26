SELECT COUNT(DISTINCT order_id) AS total_orders
FROM fact_orders
WHERE order_status = 'Completed';
