WITH country_product_sales AS (

    SELECT

        dc.country,

        dp.stock_code,

        dp.description,

        SUM(fo.revenue) AS total_revenue,

        RANK() OVER (

            PARTITION BY dc.country

            ORDER BY SUM(fo.revenue) DESC

        ) AS product_rank

    FROM fact_orders fo

    JOIN dim_customers dc
        ON fo.customer_key = dc.customer_key

    JOIN dim_products dp
        ON fo.product_key = dp.product_key

    GROUP BY

        dc.country,

        dp.stock_code,

        dp.description
)

SELECT *

FROM country_product_sales

WHERE product_rank = 1

ORDER BY country;