-- SQLite table for Payment (table: payment)
CREATE TABLE IF NOT EXISTS payment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comanda_id TEXT NOT NULL,
  method TEXT NOT NULL CHECK (method IN ('cash', 'card', 'pix', 'voucher', 'tab')),
  amount_cents INTEGER NOT NULL,
  received_at TEXT,
  notes TEXT,
  FOREIGN KEY (comanda_id) REFERENCES comanda.id
);
