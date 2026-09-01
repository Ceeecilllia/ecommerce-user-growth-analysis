-- RFM segmentation using quartile scores.
-- The analysis snapshot is one day after the final transaction date.

WITH customer_rfm AS (
    SELECT
        customer_id,
        CAST(JULIANDAY('2011-12-10') - JULIANDAY(DATE(MAX(invoice_date))) AS INTEGER) AS recency,
        COUNT(DISTINCT invoice_no) AS frequency,
        SUM(revenue) AS monetary
    FROM transactions
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        *,
        5 - NTILE(4) OVER (ORDER BY recency ASC, customer_id) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC, customer_id) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC, customer_id) AS m_score
    FROM customer_rfm
),
segmented AS (
    SELECT
        *,
        CASE
            WHEN r_score = 4 AND f_score = 4 AND m_score >= 3 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 3 AND f_score <= 2 THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating'
            ELSE 'Needs Attention'
        END AS segment
    FROM rfm_scores
),
segment_summary AS (
    SELECT
        segment,
        COUNT(*) AS customers,
        SUM(monetary) AS revenue,
        AVG(recency) AS average_recency,
        AVG(frequency) AS average_frequency,
        AVG(monetary) AS average_customer_value
    FROM segmented
    GROUP BY segment
),
totals AS (
    SELECT
        SUM(customers) AS total_customers,
        SUM(revenue) AS total_revenue
    FROM segment_summary
)
SELECT
    s.segment,
    s.customers,
    ROUND(1.0 * s.customers / t.total_customers, 4) AS customer_share,
    ROUND(s.revenue, 2) AS revenue_gbp,
    ROUND(s.revenue / t.total_revenue, 4) AS revenue_share,
    ROUND(s.average_recency, 1) AS average_recency_days,
    ROUND(s.average_frequency, 2) AS average_orders,
    ROUND(s.average_customer_value, 2) AS average_customer_value_gbp
FROM segment_summary AS s
CROSS JOIN totals AS t
ORDER BY revenue_gbp DESC;

