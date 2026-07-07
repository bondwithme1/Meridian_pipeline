-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS audit;

-- staging.transactions
CREATE TABLE IF NOT EXISTS staging.transactions (
    timestamp        TIMESTAMP NOT NULL,
    store_id         TEXT      NOT NULL,
    staff_name       TEXT      NOT NULL,
    receipt_no       TEXT      NOT NULL,
    customer_phone   TEXT,
    product_sold     TEXT      NOT NULL,
    quantity         INTEGER   NOT NULL CHECK (quantity BETWEEN 1 AND 20),
    payment_method   TEXT      NOT NULL CHECK (payment_method IN ('Cash', 'Card', 'Transfer')),
    source_sheet     TEXT      NOT NULL
);

-- staging.products
CREATE TABLE IF NOT EXISTS staging.products (
    product_id       TEXT    NOT NULL PRIMARY KEY,
    product_name     TEXT    NOT NULL,
    category         TEXT    NOT NULL,
    unit_price_ghs   NUMERIC NOT NULL CHECK (unit_price_ghs > 0),
    last_updated     DATE
);

-- staging.staff
CREATE TABLE IF NOT EXISTS staging.staff (
    staff_id         TEXT NOT NULL PRIMARY KEY,
    full_name        TEXT NOT NULL,
    role             TEXT NOT NULL,
    store_id         TEXT NOT NULL,
    store_city       TEXT,
    phone_number     TEXT
);

-- staging.managers
CREATE TABLE IF NOT EXISTS staging.managers (
    manager_id       TEXT NOT NULL PRIMARY KEY,
    full_name        TEXT NOT NULL,
    role             TEXT NOT NULL,
    store_id         TEXT NOT NULL,
    phone_number     TEXT,
    email            TEXT,
    hire_date        DATE
);

-- staging.stores
CREATE TABLE IF NOT EXISTS staging.stores (
    store_id         TEXT NOT NULL PRIMARY KEY,
    city             TEXT NOT NULL,
    region           TEXT NOT NULL
);

-- audit.validation_log
CREATE TABLE IF NOT EXISTS audit.validation_log (
    check_name       TEXT      NOT NULL,
    store_id         TEXT,
    raw_value        TEXT,
    flagged_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



------------------constrainst test

INSERT INTO staging.transactions 
(timestamp, store_id, staff_name, receipt_no, product_sold, quantity, payment_method, source_sheet)
VALUES 
(NOW(), 'S001', 'Test', 'R001', 'Rice', 25, 'Bitcoin', 'test');