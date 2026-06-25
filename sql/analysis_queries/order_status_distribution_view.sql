CREATE OR REPLACE VIEW order_status_distribution AS
SELECT
    order_status,
    COUNT(DISTINCT order_id) AS total_orders
FROM fact_orders
GROUP BY order_status;