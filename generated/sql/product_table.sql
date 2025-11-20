-- SQLite table for Product (table: product)
CREATE TABLE IF NOT EXISTS product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  description TEXT,
  cost_price_cents INTEGER,
  stock_current REAL,
  stock_minimum REAL,
  unit TEXT,
  product_type TEXT,
  active BOOLEAN DEFAULT 1,
  last_modified TEXT,
  dirty BOOLEAN DEFAULT 0,
  origin_device TEXT
);
