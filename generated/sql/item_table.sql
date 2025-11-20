-- SQLite table for Item (table: item)
CREATE TABLE IF NOT EXISTS item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  description TEXT,
  sale_price_cents INTEGER,
  unit_cost_cents INTEGER,
  prep_time_min INTEGER,
  item_type TEXT NOT NULL CHECK (item_type IN ('dish', 'drink', 'article')),
  category_id INTEGER,
  subcategory_id INTEGER,
  active BOOLEAN DEFAULT 1,
  notes TEXT,
  last_modified TEXT,
  dirty BOOLEAN DEFAULT 0,
  origin_device TEXT,
  FOREIGN KEY (category_id) REFERENCES category.id,
  FOREIGN KEY (subcategory_id) REFERENCES subcategory.id
);
