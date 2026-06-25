WITH country_product_sales AS (
    SELECT
        dc.country,
        dp.product_id,
        dp.product_name,
        SUM(fo.line_total) AS total_revenue,
        RANK() OVER (
            PARTITION BY dc.country
            ORDER BY SUM(fo.line_total) DESC
        ) AS product_rank
    FROM fact_orders fo
    JOIN dim_customers dc
        ON fo.customer_id = dc.customer_id
    JOIN dim_products dp
        ON fo.product_id = dp.product_id
    WHERE fo.order_status = 'Completed'
    GROUP BY
        dc.country,
        dp.product_id,
        dp.product_name
)
SELECT *
FROM country_product_sales
WHERE product_rank = 1
ORDER BY country;