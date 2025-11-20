-- SQLite table for Subcategory (table: subcategory)
CREATE TABLE IF NOT EXISTS subcategory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  category_id INTEGER NOT NULL,
  FOREIGN KEY (category_id) REFERENCES category.id
);
