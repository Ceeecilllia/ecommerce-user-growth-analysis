# Data setup

1. Download `Online Retail.xlsx` from the official UCI dataset page:
   https://archive.ics.uci.edu/dataset/352/online+retail
2. Place the unmodified file at:

```text
data/raw/Online Retail.xlsx
```

3. Run `notebooks/01_data_cleaning.ipynb` from the repository root.

The notebook writes the cleaned customer-level transaction table to:

```text
data/processed/online_retail_clean.csv.gz
```

Raw and processed datasets are intentionally excluded from Git because they are reproducible from the cited source.

## Landing-page A/B test

1. Download `ab_data.csv` from:
   https://www.kaggle.com/datasets/zhangluyuan/ab-testing
2. Place the unmodified file at:

```text
data/raw/ab_data.csv
```

3. Run `notebooks/05_ab_testing.ipynb`.

The two public datasets are analytically connected through the customer lifecycle but are independent sources. They are not joined at user level.

