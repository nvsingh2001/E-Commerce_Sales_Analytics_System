TRUNCATE TABLE
    fact_orders,
    dim_customers,
    dim_products,
    analytics.revenue_summary,
    analytics.customer_retention,
    analytics.product_performance
RESTART IDENTITY CASCADE;
