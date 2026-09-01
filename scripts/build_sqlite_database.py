from pathlib import Path
import sqlite3
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "online_retail_clean.csv.gz"
DATABASE_PATH = ROOT / "data" / "processed" / "online_retail.db"
SCHEMA_PATH = ROOT / "sql" / "00_schema.sql"


def main() -> None:
    df = pd.read_csv(
        DATA_PATH,
        compression="gzip",
        parse_dates=["InvoiceDate"],
        dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": str},
    )
    df.columns = [
        "invoice_no",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
        "revenue",
    ]
    df["invoice_date"] = df["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA_PATH.read_text())
        df.to_sql("transactions", connection, if_exists="append", index=False, chunksize=20_000)
        row_count = connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]

    if row_count != len(df):
        raise RuntimeError(f"Expected {len(df):,} rows, loaded {row_count:,} rows.")
    print(f"Loaded {row_count:,} rows into {DATABASE_PATH}")


if __name__ == "__main__":
    main()

