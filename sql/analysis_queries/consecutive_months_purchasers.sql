WITH customer_orders AS (

    SELECT

        customer_key,

        DATE_TRUNC(
            'month',
            order_date
        ) AS purchase_month

    FROM fact_orders

    GROUP BY
        customer_key,
        purchase_month
)

SELECT DISTINCT

    c1.customer_key

FROM customer_orders c1

JOIN customer_orders c2

ON c1.customer_key = c2.customer_key

AND c2.purchase_month =
    c1.purchase_month + INTERVAL '1 month';