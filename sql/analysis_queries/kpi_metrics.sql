SELECT 
    (SELECT SUM(line_total) FROM fact_orders WHERE order_status = 'Completed') as total_revenue,
    (SELECT COUNT(DISTINCT order_id) FROM fact_orders WHERE order_status = 'Completed') as total_orders,
    (SELECT COUNT(DISTINCT customer_id) FROM dim_customers) as total_customers,
    (SELECT COUNT(*) FROM analytics.customer_retention WHERE total_orders >= 2) as repeat_customers,
    (SELECT COUNT(*) FROM analytics.customer_retention) as total_retention_customers;
