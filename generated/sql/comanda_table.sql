-- SQLite table for Comanda (table: comanda)
CREATE TABLE IF NOT EXISTS comanda (
  id TEXT PRIMARY KEY,
  table_id INTEGER,
  status TEXT NOT NULL CHECK (status IN ('open', 'closed', 'cancelled')),
  opened_at TEXT,
  closed_at TEXT,
  subtotal_cents INTEGER,
  total_cents INTEGER,
  notes TEXT,
  last_modified TEXT,
  dirty BOOLEAN DEFAULT 0,
  origin_device TEXT,
  FOREIGN KEY (table_id) REFERENCES dining_table.id
);
