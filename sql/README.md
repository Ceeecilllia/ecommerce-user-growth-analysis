# SQL analysis

The SQL module uses SQLite and the cleaned customer-level transaction table.

| File | Purpose |
|---|---|
| `00_schema.sql` | Transaction table and indexes |
| `01_kpi_summary.sql` | Revenue, orders, customers, AOV, and repeat rate |
| `02_monthly_performance.sql` | Monthly trend and month-over-month growth |
| `03_repeat_purchase.sql` | Right-censoring-aware 7-day and 30-day repeat purchase |
| `04_cohort_retention.sql` | Long-format monthly cohort retention |
| `05_rfm_segmentation.sql` | Quartile RFM scoring and lifecycle segments |

Queries use named CTEs to keep intermediate tables visible and interview-friendly.

