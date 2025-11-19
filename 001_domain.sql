-- BOTECOPRO — SQLite DATABASE SCHEMA (Professional Version)
-- All tables carefully revised for offline-first operations
-- Language: English
-- Notes:
--  * SQLite AUTO-INCREMENT uses INTEGER PRIMARY KEY
--  * UUIDs stored as TEXT, generated at app layer
--  * All timestamps use TEXT (ISO-8601) with CURRENT_TIMESTAMP
--  * All foreign keys enforce cascade rules as needed for data integrity
PRAGMA foreign_keys = ON;

-----------------------------------------------------------------------
-- UTIL: GLOBAL EVENT STORE (DDD / OFFLINE SYNC)
-----------------------------------------------------------------------
CREATE TABLE domain_event (
    event_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT NOT NULL,
    aggregate_type  TEXT,
    aggregate_id    TEXT,
    payload         TEXT NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    processed       INTEGER DEFAULT 0,
    origin_device   TEXT
);

CREATE INDEX idx_event_type ON domain_event(event_type);
CREATE INDEX idx_event_aggregate ON domain_event(aggregate_type, aggregate_id);

-----------------------------------------------------------------------
-- CATEGORY & SUBCATEGORY
-----------------------------------------------------------------------
CREATE TABLE category (
    category_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL
);

CREATE TABLE subcategory (
    subcategory_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id     INTEGER NOT NULL,
    name            TEXT NOT NULL,

    FOREIGN KEY (category_id)
        REFERENCES category(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-----------------------------------------------------------------------
-- PRODUCTS (INGREDIENTS / ESTOQUE)
-----------------------------------------------------------------------
CREATE TABLE product (
    product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    description     TEXT,
    cost_price_cents INTEGER DEFAULT 0,
    stock_current   REAL DEFAULT 0,          -- pode ser fracionado (g, ml)
    stock_minimum   REAL DEFAULT 0,
    unit            TEXT,                    -- g, kg, ml, unit
    product_type    TEXT CHECK(product_type IN ('ingredient','resale')),
    active          INTEGER DEFAULT 1,

    last_modified   TEXT,
    dirty           INTEGER DEFAULT 1,
    origin_device   TEXT
);

CREATE INDEX idx_product_name ON product(name);

-----------------------------------------------------------------------
-- SUPPLIERS
-----------------------------------------------------------------------
CREATE TABLE supplier (
    supplier_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    notes           TEXT
);

CREATE TABLE supplier_product (
    product_id      INTEGER NOT NULL,
    supplier_id     INTEGER NOT NULL,
    price_cents     INTEGER,
    notes           TEXT,

    PRIMARY KEY (product_id, supplier_id),

    FOREIGN KEY (product_id)
        REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    FOREIGN KEY (supplier_id)
        REFERENCES supplier(supplier_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-----------------------------------------------------------------------
-- MENU ITEMS (DISH / DRINK / ARTICLE)
-----------------------------------------------------------------------
CREATE TABLE item (
    item_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    description     TEXT,
    sale_price_cents INTEGER,
    unit_cost_cents  INTEGER,
    prep_time_min   INTEGER,
    item_type       TEXT NOT NULL CHECK(item_type IN ('dish','drink','article')),
    category_id     INTEGER,
    subcategory_id  INTEGER,
    active          INTEGER DEFAULT 1,
    notes           TEXT,

    FOREIGN KEY (category_id)
        REFERENCES category(category_id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    FOREIGN KEY (subcategory_id)
        REFERENCES subcategory(subcategory_id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    last_modified   TEXT,
    dirty           INTEGER DEFAULT 1,
    origin_device   TEXT
);

CREATE INDEX idx_item_name ON item(name);

-- ITEM COMPOSITION: recipes linking items to products
CREATE TABLE item_product (
    item_id         INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        REAL NOT NULL,

    PRIMARY KEY (item_id, product_id),

    FOREIGN KEY (item_id)
        REFERENCES item(item_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-----------------------------------------------------------------------
-- DINING TABLES
-----------------------------------------------------------------------
CREATE TABLE dining_table (
    table_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    table_num   INTEGER NOT NULL,
    seats       INTEGER,
    available   INTEGER DEFAULT 1
);

CREATE UNIQUE INDEX idx_table_number ON dining_table(table_num);

-----------------------------------------------------------------------
-- COMANDA (ORDER SESSION, UUID-BASED)
-----------------------------------------------------------------------
CREATE TABLE comanda (
    comanda_id      TEXT PRIMARY KEY,       -- UUID
    table_id        INTEGER,
    status          TEXT CHECK(status IN ('open','closed','cancelled')),
    opened_at       TEXT DEFAULT CURRENT_TIMESTAMP,
    closed_at       TEXT,
    subtotal_cents  INTEGER DEFAULT 0,
    total_cents     INTEGER DEFAULT 0,
    notes           TEXT,

    FOREIGN KEY (table_id)
        REFERENCES dining_table(table_id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    last_modified   TEXT,
    dirty           INTEGER DEFAULT 1,
    origin_device   TEXT
);

-----------------------------------------------------------------------
-- EMPLOYEES & CUSTOMERS
-----------------------------------------------------------------------
CREATE TABLE employee (
    employee_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT,
    tax_id          TEXT,
    address         TEXT,
    city            TEXT,
    postal_code     TEXT,
    phone           TEXT,
    email           TEXT,
    role            TEXT,
    hired_on        TEXT,
    hourly_rate_cents INTEGER
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

-----------------------------------------------------------------------
-- ORDER (HEADER)
-----------------------------------------------------------------------
CREATE TABLE order_header (
    order_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id      TEXT NOT NULL,
    origin          TEXT CHECK(origin IN ('table','takeaway','delivery')),
    employee_id     INTEGER,
    customer_id     INTEGER,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    status          TEXT CHECK(status IN ('open','preparing','ready','delivered','cancelled')),
    notes           TEXT,

    FOREIGN KEY (comanda_id)
        REFERENCES comanda(comanda_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    FOREIGN KEY (employee_id)
        REFERENCES employee(employee_id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customer(customer_id)
        ON UPDATE CASCADE ON DELETE SET NULL,

    last_modified   TEXT,
    dirty           INTEGER DEFAULT 1,
    origin_device   TEXT
);

CREATE INDEX idx_order_by_comanda ON order_header(comanda_id);

-----------------------------------------------------------------------
-- ORDER ITEMS
-----------------------------------------------------------------------
CREATE TABLE order_item (
    order_item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id          INTEGER NOT NULL,
    item_id           INTEGER NOT NULL,
    quantity          INTEGER NOT NULL,
    unit_price_cents  INTEGER,
    discount_percent  REAL DEFAULT 0,
    tax_percent       REAL DEFAULT 0,
    total_cents       INTEGER,
    notes             TEXT,

    FOREIGN KEY (order_id)
        REFERENCES order_header(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    FOREIGN KEY (item_id)
        REFERENCES item(item_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    last_modified     TEXT,
    dirty             INTEGER DEFAULT 1,
    origin_device     TEXT
);

CREATE INDEX idx_order_item_order ON order_item(order_id);

-----------------------------------------------------------------------
-- INVOICES (FISCAL CALCULATIONS)
-----------------------------------------------------------------------
CREATE TABLE invoice (
    invoice_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id      TEXT NOT NULL,
    subtotal_cents  INTEGER,
    tax_total_cents INTEGER,
    total_cents     INTEGER,
    closed_at       TEXT,

    FOREIGN KEY (comanda_id)
        REFERENCES comanda(comanda_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-----------------------------------------------------------------------
-- PAYMENTS (MULTIPLE METHODS)
-----------------------------------------------------------------------
CREATE TABLE payment (
    payment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id       TEXT NOT NULL,
    method           TEXT CHECK(method IN ('cash','card','pix','voucher','tab')),
    amount_cents     INTEGER NOT NULL,
    received_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    notes            TEXT,

    FOREIGN KEY (comanda_id)
        REFERENCES comanda(comanda_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE payment_split (
    split_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id      INTEGER NOT NULL,
    payee_name      TEXT,
    amount_cents    INTEGER NOT NULL,

    FOREIGN KEY (payment_id)
        REFERENCES payment(payment_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-----------------------------------------------------------------------
-- STOCK MOVEMENTS (AUDITABLE)
-----------------------------------------------------------------------
CREATE TABLE stock_movement (
    movement_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id       INTEGER NOT NULL,
    quantity         REAL NOT NULL,
    movement_type    TEXT NOT NULL CHECK(movement_type IN ('in','out','adjustment')),
    reason           TEXT,
    related_order_item INTEGER,
    created_at       TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES product(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-----------------------------------------------------------------------
-- KITCHEN/BAR TICKETS
-----------------------------------------------------------------------
CREATE TABLE kitchen_ticket (
    ticket_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        INTEGER NOT NULL,
    status          TEXT CHECK(status IN ('new','cooking','ready','delivered')),
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES order_header(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE kitchen_ticket_item (
    ticket_item_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id       INTEGER NOT NULL,
    order_item_id   INTEGER NOT NULL,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ticket_id)
        REFERENCES kitchen_ticket(ticket_id)
        ON UPDATE CASCADE ON DELETE CASCADE,

    FOREIGN KEY (order_item_id)
        REFERENCES order_item(order_item_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
