-- SQLite table for SupplierProduct (table: supplier_product)
CREATE TABLE IF NOT EXISTS supplier_product (
  product_id INTEGER,
  supplier_id INTEGER,
  price_cents INTEGER,
  notes TEXT,
  FOREIGN KEY (product_id) REFERENCES product.id,
  FOREIGN KEY (supplier_id) REFERENCES supplier.id,
  PRIMARY KEY (product_id, supplier_id)
);
