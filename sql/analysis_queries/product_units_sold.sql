SELECT 
    dp.product_id, 
    dp.product_name, 
    SUM(pp.units_sold) as total_units,
    SUM(pp.total_revenue) as total_revenue
FROM analytics.product_performance pp
JOIN dim_products dp ON pp.product_id = dp.product_id
GROUP BY dp.product_id, dp.product_name;
