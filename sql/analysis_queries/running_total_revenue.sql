SELECT

    DATE_TRUNC(
        'month',
        order_date
    ) AS revenue_month,

    SUM(revenue) AS monthly_revenue,

    SUM(
        SUM(revenue)
    ) OVER (

        ORDER BY DATE_TRUNC(
            'month',
            order_date
        )

    ) AS running_total

FROM fact_orders

GROUP BY revenue_month

ORDER BY revenue_month;