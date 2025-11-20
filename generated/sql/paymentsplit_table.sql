-- SQLite table for PaymentSplit (table: payment_split)
CREATE TABLE IF NOT EXISTS payment_split (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  payment_id INTEGER NOT NULL,
  payee_name TEXT,
  amount_cents INTEGER NOT NULL,
  FOREIGN KEY (payment_id) REFERENCES payment.id
);
