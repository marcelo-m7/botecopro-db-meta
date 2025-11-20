-- SQLite table for Order (table: order)
CREATE TABLE IF NOT EXISTS order (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comanda_id TEXT NOT NULL,
  employee_id INTEGER,
  customer_id INTEGER,
  origin TEXT NOT NULL CHECK (origin IN ('table', 'takeaway', 'delivery')),
  status TEXT NOT NULL CHECK (status IN ('open', 'preparing', 'ready', 'delivered', 'cancelled')),
  created_at TEXT,
  notes TEXT,
  last_modified TEXT,
  dirty BOOLEAN DEFAULT 0,
  origin_device TEXT,
  FOREIGN KEY (comanda_id) REFERENCES comanda.id,
  FOREIGN KEY (employee_id) REFERENCES employee.id,
  FOREIGN KEY (customer_id) REFERENCES customer.id
);
