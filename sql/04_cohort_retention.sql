-- Long-format monthly cohort retention table.

WITH customer_first_purchase AS (
    SELECT
        customer_id,
        DATE(MIN(invoice_date), 'start of month') AS cohort_month
    FROM transactions
    GROUP BY customer_id
),
customer_monthly_activity AS (
    SELECT DISTINCT
        customer_id,
        DATE(invoice_date, 'start of month') AS activity_month
    FROM transactions
),
cohort_activity AS (
    SELECT
        a.customer_id,
        f.cohort_month,
        a.activity_month,
        (
            (CAST(STRFTIME('%Y', a.activity_month) AS INTEGER) - CAST(STRFTIME('%Y', f.cohort_month) AS INTEGER)) * 12
            + CAST(STRFTIME('%m', a.activity_month) AS INTEGER)
            - CAST(STRFTIME('%m', f.cohort_month) AS INTEGER)
        ) AS cohort_index
    FROM customer_monthly_activity AS a
    JOIN customer_first_purchase AS f
        ON a.customer_id = f.customer_id
),
retained_customers AS (
    SELECT
        cohort_month,
        cohort_index,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM cohort_activity
    GROUP BY cohort_month, cohort_index
),
cohort_sizes AS (
    SELECT
        cohort_month,
        active_customers AS cohort_size
    FROM retained_customers
    WHERE cohort_index = 0
)
SELECT
    r.cohort_month,
    r.cohort_index,
    s.cohort_size,
    r.active_customers,
    ROUND(1.0 * r.active_customers / s.cohort_size, 4) AS retention_rate
FROM retained_customers AS r
JOIN cohort_sizes AS s
    ON r.cohort_month = s.cohort_month
ORDER BY r.cohort_month, r.cohort_index;

