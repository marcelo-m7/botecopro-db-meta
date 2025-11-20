-- SQLite table for DiningTable (table: dining_table)
CREATE TABLE IF NOT EXISTS dining_table (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_num INTEGER,
  seats INTEGER,
  available BOOLEAN DEFAULT 1
);
