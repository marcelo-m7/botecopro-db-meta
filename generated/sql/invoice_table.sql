-- SQLite table for Invoice (table: invoice)
CREATE TABLE IF NOT EXISTS invoice (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comanda_id TEXT NOT NULL,
  subtotal_cents INTEGER,
  tax_total_cents INTEGER,
  total_cents INTEGER,
  closed_at TEXT,
  FOREIGN KEY (comanda_id) REFERENCES comanda.id
);
