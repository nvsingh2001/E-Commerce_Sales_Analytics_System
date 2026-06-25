SELECT 
    order_id, 
    SUM(line_total) as order_value
FROM fact_orders
WHERE order_status = 'Completed'
GROUP BY order_id
HAVING SUM(line_total) > 0;
