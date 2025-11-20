-- SQLite table for KitchenTicket (table: kitchen_ticket)
CREATE TABLE IF NOT EXISTS kitchen_ticket (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('new', 'cooking', 'ready', 'delivered')),
  created_at TEXT,
  FOREIGN KEY (order_id) REFERENCES order.id
);
