SELECT

    dc.customer_segment,

    AVG(fo.revenue) AS average_order_value

FROM fact_orders fo

JOIN dim_customers dc
    ON fo.customer_key = dc.customer_key

GROUP BY dc.customer_segment

ORDER BY average_order_value DESC;
