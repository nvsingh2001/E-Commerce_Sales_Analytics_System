SELECT 
    country, 
    month, 
    SUM(total_revenue) as revenue
FROM analytics.revenue_summary
GROUP BY country, month;
