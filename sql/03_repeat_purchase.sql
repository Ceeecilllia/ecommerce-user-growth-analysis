-- 7-day and 30-day repeat purchase rates with complete observation windows.
-- Acquisition is the first distinct order; repeat purchase is the second distinct order.

WITH parameters AS (
    SELECT MAX(invoice_date) AS data_end_timestamp
    FROM transactions
),
distinct_orders AS (
    SELECT
        customer_id,
        invoice_no,
        MIN(invoice_date) AS order_date
    FROM transactions
    GROUP BY customer_id, invoice_no
),
ranked_orders AS (
    SELECT
        customer_id,
        invoice_no,
        order_date,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_date, invoice_no
        ) AS order_number
    FROM distinct_orders
),
first_second_orders AS (
    SELECT
        customer_id,
        MAX(CASE WHEN order_number = 1 THEN order_date END) AS first_order_date,
        MAX(CASE WHEN order_number = 2 THEN order_date END) AS second_order_date
    FROM ranked_orders
    WHERE order_number <= 2
    GROUP BY customer_id
),
repeat_flags AS (
    SELECT
        customer_id,
        first_order_date,
        second_order_date,
        JULIANDAY(second_order_date) - JULIANDAY(first_order_date) AS days_to_second_order,
        CASE WHEN first_order_date <= DATETIME(p.data_end_timestamp, '-7 days') THEN 1 ELSE 0 END AS eligible_7d,
        CASE WHEN first_order_date <= DATETIME(p.data_end_timestamp, '-30 days') THEN 1 ELSE 0 END AS eligible_30d
    FROM first_second_orders
    CROSS JOIN parameters AS p
),
window_summary AS (
    SELECT
        '7-day' AS measurement_window,
        SUM(eligible_7d) AS eligible_customers,
        SUM(CASE WHEN eligible_7d = 1 AND days_to_second_order > 0 AND days_to_second_order <= 7 THEN 1 ELSE 0 END) AS repeat_customers
    FROM repeat_flags

    UNION ALL

    SELECT
        '30-day' AS measurement_window,
        SUM(eligible_30d) AS eligible_customers,
        SUM(CASE WHEN eligible_30d = 1 AND days_to_second_order > 0 AND days_to_second_order <= 30 THEN 1 ELSE 0 END) AS repeat_customers
    FROM repeat_flags
)
SELECT
    measurement_window,
    eligible_customers,
    repeat_customers,
    ROUND(1.0 * repeat_customers / eligible_customers, 4) AS repeat_purchase_rate
FROM window_summary;
