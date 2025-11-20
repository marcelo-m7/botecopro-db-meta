-- SQLite table for OrderItem (table: order_item)
CREATE TABLE IF NOT EXISTS order_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  item_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price_cents INTEGER NOT NULL,
  discount_percent REAL,
  tax_percent REAL,
  total_cents INTEGER,
  notes TEXT,
  last_modified TEXT,
  dirty BOOLEAN DEFAULT 0,
  origin_device TEXT,
  FOREIGN KEY (order_id) REFERENCES order.id,
  FOREIGN KEY (item_id) REFERENCES item.id
);
