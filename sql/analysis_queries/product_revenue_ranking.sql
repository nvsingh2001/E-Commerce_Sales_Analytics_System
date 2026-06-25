SELECT

    dp.stock_code,

    dp.description,

    SUM(fo.revenue) AS total_revenue,

    RANK() OVER (

        ORDER BY SUM(fo.revenue) DESC

    ) AS revenue_rank

FROM fact_orders fo

JOIN dim_products dp
    ON fo.product_key = dp.product_key

GROUP BY

    dp.stock_code,

    dp.description;