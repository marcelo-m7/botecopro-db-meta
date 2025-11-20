-- SQLite table for KitchenTicketItem (table: kitchen_ticket_item)
CREATE TABLE IF NOT EXISTS kitchen_ticket_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ticket_id INTEGER NOT NULL,
  order_item_id INTEGER NOT NULL,
  FOREIGN KEY (ticket_id) REFERENCES kitchen_ticket.id,
  FOREIGN KEY (order_item_id) REFERENCES order_item.id
);
