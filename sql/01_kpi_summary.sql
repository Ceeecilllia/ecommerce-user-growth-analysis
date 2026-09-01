-- Executive KPI summary.
-- Repeat customer rate uses distinct completed orders per identified customer.

WITH order_level AS (
    SELECT
        invoice_no,
        customer_id,
        SUM(revenue) AS order_revenue
    FROM transactions
    GROUP BY invoice_no, customer_id
),
customer_level AS (
    SELECT
        customer_id,
        COUNT(DISTINCT invoice_no) AS order_count,
        SUM(order_revenue) AS customer_revenue
    FROM order_level
    GROUP BY customer_id
),
overall AS (
    SELECT
        (SELECT SUM(revenue) FROM transactions) AS total_revenue,
        (SELECT COUNT(*) FROM order_level) AS total_orders,
        (SELECT COUNT(*) FROM customer_level) AS total_customers,
        (SELECT SUM(quantity) FROM transactions) AS units_sold,
        (SELECT COUNT(*) FROM customer_level WHERE order_count >= 2) AS repeat_customers
)
SELECT
    ROUND(total_revenue, 2) AS total_revenue_gbp,
    total_orders,
    total_customers,
    units_sold,
    ROUND(total_revenue / total_orders, 2) AS average_order_value_gbp,
    ROUND(1.0 * total_orders / total_customers, 2) AS orders_per_customer,
    repeat_customers,
    ROUND(1.0 * repeat_customers / total_customers, 4) AS repeat_customer_rate
FROM overall;

