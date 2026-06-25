SELECT
    dp.product_id,
    dp.product_name
FROM dim_products dp
WHERE NOT EXISTS (
    SELECT 1
    FROM fact_orders fo
    WHERE fo.product_id = dp.product_id
      AND fo.order_date >= (
          SELECT MAX(order_date)
          FROM fact_orders
      ) - INTERVAL '60 days'
);