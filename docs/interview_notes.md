# Interview Notes

## Technical challenge: misleading product rankings

Direct product ranking by revenue was distorted by a single wholesale order worth approximately £168K. Administrative lines such as `POSTAGE` and `Manual` also appeared among top products.

Resolution:

1. Preserved the raw ranking for auditability.
2. Flagged administrative stock codes separately.
3. Distinguished one-off wholesale demand from recurring merchandise performance.
4. Built the portfolio chart using merchandise appearing in at least 10 distinct orders.
5. Documented the business interpretation instead of silently deleting influential records.

## Technical challenge: incomplete retention windows

Customers acquired near the dataset end do not have a full 7-day or 30-day observation period. Treating them as non-retained would bias retention downward.

Resolution:

1. Defined the first distinct order as acquisition.
2. Calculated time to the second distinct order.
3. Included customers only when the complete measurement window was observable.
4. Reported eligible-customer counts alongside each retention rate.

## Technical challenge: tied values in RFM quantiles

Many customers have the same order frequency, especially a frequency of one. Applying `qcut` directly can create duplicate quantile edges or unstable groups.

Resolution:

1. Ranked Recency, Frequency, and Monetary values before quartile assignment.
2. Reverse-scored Recency so a more recent purchase receives a higher score.
3. Applied segment rules in priority order to guarantee mutually exclusive coverage.
4. Kept Monetary score as both a segmentation input and a separate high-value flag.

## Technical challenge: SQL and Python boundary consistency

The first SQL repeat-purchase query compared calendar dates, while Python used exact timestamps. This created small differences in eligible-customer counts near the 7-day and 30-day cutoffs.

Resolution:

1. Derived the dataset-end timestamp dynamically in SQL.
2. Applied exact timestamp offsets rather than truncating to calendar dates.
3. Reconciled KPI, monthly, repeat-purchase, and cohort outputs across Python and SQL.
4. Documented that SQLite `NTILE` can place one boundary customer differently from pandas `qcut` when quartiles contain tied values and unequal remainder sizes.

## Technical challenge: invalid A/B assignment and duplicate users

The raw experiment contains users whose assigned group does not match the page shown, plus repeated user observations. Keeping them would violate the intended treatment definition and independence assumption.

Resolution:

1. Retained only control–old-page and treatment–new-page matches.
2. Sorted by timestamp and kept the first valid observation per user.
3. Verified unique users and near-even traffic allocation after cleaning.
4. Reported effect size, confidence interval, and p-value rather than relying on conversion-rate direction alone.
