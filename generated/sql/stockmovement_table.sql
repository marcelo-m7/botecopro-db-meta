-- SQLite table for StockMovement (table: stock_movement)
CREATE TABLE IF NOT EXISTS stock_movement (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  quantity REAL NOT NULL,
  movement_type TEXT NOT NULL CHECK (movement_type IN ('in', 'out', 'adjustment')),
  reason TEXT,
  related_order_item INTEGER,
  created_at TEXT,
  FOREIGN KEY (product_id) REFERENCES product.id,
  FOREIGN KEY (related_order_item) REFERENCES order_item.id
);
