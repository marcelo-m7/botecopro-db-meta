-- BOTECOPRO — SQLite DATABASE SCHEMA (Professional Version)
-- All tables carefully revised for offline-first operations
-- Language: English
-- Notes:
--  * SQLite AUTO-INCREMENT uses INTEGER PRIMARY KEY
--  * UUIDs stored as TEXT, generated at app layer
--  * All timestamps use TEXT (ISO-8601) with CURRENT_TIMESTAMP
--  * All foreign keys enforce cascade rules as needed for data integrity

PRAGMA foreign_keys = ON;

------------------------------------------------------------------------------
-- CATEGORY & SUBCATEGORY
------------------------------------------------------------------------------
CREATE TABLE category (
    category_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL
);

CREATE TABLE subcategory (
    subcategory_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id     INTEGER NOT NULL,
    name            TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

------------------------------------------------------------------------------
-- PRODUCTS / INGREDIENTS
------------------------------------------------------------------------------
CREATE TABLE product (
    product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    description     TEXT,
    cost_price      REAL,
    stock_current   INTEGER DEFAULT 0,
    stock_minimum   INTEGER DEFAULT 0,
    unit            TEXT,               -- g, kg, ml, unit
    product_type    TEXT,               -- ingredient, resale, etc.
    active          INTEGER DEFAULT 1
);

CREATE TABLE supplier (
    supplier_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    notes           TEXT
);

-- Supplier price list and association
CREATE TABLE supplier_product (
    product_id      INTEGER NOT NULL,
    supplier_id     INTEGER NOT NULL,
    price           REAL,
    notes           TEXT,

    PRIMARY KEY (product_id, supplier_id),

    FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

------------------------------------------------------------------------------
-- ITEM (Menu item: dish / drink / article)
------------------------------------------------------------------------------
CREATE TABLE item (
    item_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    description     TEXT,
    sale_price      REAL,
    unit_cost       REAL,
    prep_time_min   INTEGER,            -- in minutes
    item_type       TEXT NOT NULL CHECK (item_type IN ('dish','drink','article')),
    category_id     INTEGER,
    subcategory_id  INTEGER,
    active          INTEGER DEFAULT 1,
    notes           TEXT,

    FOREIGN KEY (category_id) REFERENCES category(category_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (subcategory_id) REFERENCES subcategory(subcategory_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- Composition: item uses multiple products
CREATE TABLE item_product (
    item_id     INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    REAL NOT NULL,

    PRIMARY KEY (item_id, product_id),

    FOREIGN KEY (item_id) REFERENCES item(item_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

------------------------------------------------------------------------------
-- TABLES (PHYSICAL TABLES IN RESTAURANT)
------------------------------------------------------------------------------
CREATE TABLE dining_table (
    table_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    table_num   INTEGER NOT NULL,
    seats       INTEGER,
    available   INTEGER DEFAULT 1
);

------------------------------------------------------------------------------
-- COMANDA (Order session)
------------------------------------------------------------------------------
CREATE TABLE comanda (
    comanda_id      TEXT PRIMARY KEY,      -- UUID string
    table_id        INTEGER,
    status          TEXT,                  -- open, closed, canceled
    opened_at       TEXT DEFAULT CURRENT_TIMESTAMP,
    closed_at       TEXT,
    total_amount    REAL DEFAULT 0,

    FOREIGN KEY (table_id) REFERENCES dining_table(table_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

------------------------------------------------------------------------------
-- EMPLOYEES & CUSTOMERS
------------------------------------------------------------------------------
CREATE TABLE employee (
    employee_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT,
    tax_id              TEXT,
    address             TEXT,
    city                TEXT,
    postal_code         TEXT,
    phone               TEXT,
    email               TEXT,
    role                TEXT,
    hired_on            TEXT,
    hourly_rate         REAL
);

CREATE TABLE customer (
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT,
    tax_id          TEXT,
    address         TEXT,
    city            TEXT,
    postal_code     TEXT,
    customer_type   TEXT
);

------------------------------------------------------------------------------
-- ORDER (Pedido)
------------------------------------------------------------------------------
CREATE TABLE order_header (
    order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id      TEXT NOT NULL,
    origin          TEXT,                  -- table, takeaway, delivery
    employee_id     INTEGER,
    customer_id     INTEGER,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    status          TEXT,
    notes           TEXT,

    FOREIGN KEY (comanda_id) REFERENCES comanda(comanda_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- Order Items
CREATE TABLE order_item (
    order_item_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER NOT NULL,
    item_id        INTEGER NOT NULL,
    quantity       INTEGER NOT NULL,
    unit_price     REAL,
    tax_percent    REAL,
    discount_percent REAL,
    total_value    REAL,
    notes          TEXT,

    FOREIGN KEY (order_id) REFERENCES order_header(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item(item_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

------------------------------------------------------------------------------
-- INVOICE
------------------------------------------------------------------------------
CREATE TABLE invoice (
    invoice_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id       TEXT NOT NULL,
    subtotal         REAL,
    tax_total        REAL,
    total_amount     REAL,
    closed_at        TEXT,
    tax_food         REAL,
    tax_drink        REAL,

    FOREIGN KEY (comanda_id) REFERENCES comanda(comanda_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
