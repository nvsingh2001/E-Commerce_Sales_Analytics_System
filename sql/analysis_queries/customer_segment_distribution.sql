SELECT 
    customer_segment, 
    COUNT(*) as count
FROM dim_customers
WHERE customer_segment IS NOT NULL
GROUP BY customer_segment;
