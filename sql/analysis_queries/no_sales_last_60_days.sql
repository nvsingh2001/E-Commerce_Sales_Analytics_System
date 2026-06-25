SELECT

    dp.stock_code,

    dp.description

FROM dim_products dp

WHERE NOT EXISTS (

    SELECT 1

    FROM fact_orders fo

    WHERE
        fo.product_key = dp.product_key

        AND fo.order_date >= (

            SELECT MAX(order_date)

            FROM fact_orders

        ) - INTERVAL '60 days'
);