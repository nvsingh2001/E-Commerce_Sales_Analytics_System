WITH customer_orders AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', order_date) AS purchase_month
    FROM fact_orders
    WHERE order_status = 'Completed' AND customer_id IS NOT NULL
    GROUP BY
        customer_id,
        purchase_month
)
SELECT DISTINCT
    c1.customer_id
FROM customer_orders c1
JOIN customer_orders c2
    ON c1.customer_id = c2.customer_id
    AND c2.purchase_month = c1.purchase_month + INTERVAL '1 month';