-- Monthly revenue, orders, customers, units, AOV, and month-over-month growth.
-- 2010-12 and 2011-12 are partial months and should not be compared with full months.

WITH monthly_base AS (
    SELECT
        STRFTIME('%Y-%m', invoice_date) AS invoice_month,
        SUM(revenue) AS revenue,
        COUNT(DISTINCT invoice_no) AS orders,
        COUNT(DISTINCT customer_id) AS active_customers,
        SUM(quantity) AS units
    FROM transactions
    GROUP BY STRFTIME('%Y-%m', invoice_date)
),
monthly_with_lag AS (
    SELECT
        *,
        LAG(revenue) OVER (ORDER BY invoice_month) AS previous_month_revenue
    FROM monthly_base
)
SELECT
    invoice_month,
    ROUND(revenue, 2) AS revenue_gbp,
    orders,
    active_customers,
    units,
    ROUND(revenue / orders, 2) AS average_order_value_gbp,
    ROUND(
        (revenue - previous_month_revenue) / NULLIF(previous_month_revenue, 0),
        4
    ) AS revenue_growth_rate
FROM monthly_with_lag
ORDER BY invoice_month;

