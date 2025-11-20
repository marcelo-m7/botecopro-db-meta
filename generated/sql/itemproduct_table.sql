-- SQLite table for ItemProduct (table: item_product)
CREATE TABLE IF NOT EXISTS item_product (
  item_id INTEGER,
  product_id INTEGER,
  quantity REAL NOT NULL,
  FOREIGN KEY (item_id) REFERENCES item.id,
  FOREIGN KEY (product_id) REFERENCES product.id,
  PRIMARY KEY (item_id, product_id)
);
