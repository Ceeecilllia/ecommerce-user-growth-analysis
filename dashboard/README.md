# E-commerce User Growth Dashboard

## Dashboard purpose

Provide a recruiter-friendly view of business performance, customer retention, and customer value.

## Included views

1. KPI cards: revenue, orders, customers, AOV, repeat customer rate
2. Monthly revenue trend using complete months only
3. New versus returning customer revenue
4. RFM segment revenue contribution
5. Top international markets
6. Monthly cohort retention heatmap

## Tableau data sources

Connect Tableau to the CSV files in `dashboard/tableau_data/`:

- `kpi_summary.csv`
- `monthly_performance.csv`
- `new_returning_revenue.csv`
- `international_markets.csv`
- `rfm_segment_summary.csv`
- `cohort_retention_long.csv`

## Suggested Tableau layout

- Canvas: 1,600 × 900, fixed size
- Top: title and five KPI cards
- Middle left: monthly revenue line
- Middle right: RFM revenue contribution
- Bottom left: new/returning stacked bars
- Bottom middle: international market bars
- Bottom right: cohort retention heatmap

## Recommended interactions

- Month filter controlling monthly trend and new/returning revenue
- Segment selection highlighting the RFM chart
- Country filter for geographic drill-down
- Tooltip fields: revenue, orders, customers, AOV, and revenue share

## Data notes

- Cancelled orders, non-positive quantities/prices, exact duplicates, and anonymous customers are excluded.
- December 2010 and December 2011 are partial months; the primary trend uses January–November 2011.
- The dashboard preview is generated reproducibly by `scripts/build_dashboard.py`.

