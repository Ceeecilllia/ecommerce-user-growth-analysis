DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    invoice_no   TEXT NOT NULL,
    stock_code   TEXT NOT NULL,
    description  TEXT,
    quantity     INTEGER NOT NULL,
    invoice_date TEXT NOT NULL,
    unit_price   REAL NOT NULL,
    customer_id  TEXT NOT NULL,
    country      TEXT NOT NULL,
    revenue      REAL NOT NULL
);

CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_invoice ON transactions(invoice_no);
CREATE INDEX idx_transactions_date ON transactions(invoice_date);

