CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.transactions (
    timestamp                      TEXT,
    store_id                       TEXT,
    staff_name                     TEXT,
    receipt_no                     TEXT,
    customer_phone_number_optional TEXT,
    product_sold                   TEXT,
    quantity                       TEXT,
    payment_method                 TEXT,
    source_sheet                   TEXT
);

CREATE TABLE IF NOT EXISTS raw.products (
    product_id     TEXT,
    product_name   TEXT,
    category       TEXT,
    unit_price_ghs TEXT,
    last_updated   TEXT
);

CREATE TABLE IF NOT EXISTS raw.staff (
    staff_id     TEXT,
    full_name    TEXT,
    role         TEXT,
    store_id     TEXT,
    store_city   TEXT,
    phone_number TEXT
);

CREATE TABLE IF NOT EXISTS raw.managers (
    manager_id   TEXT,
    full_name    TEXT,
    role         TEXT,
    store_id     TEXT,
    phone_number TEXT,
    email        TEXT,
    hire_date    TEXT
);

CREATE TABLE IF NOT EXISTS raw.stores (
    store_id TEXT,
    city     TEXT,
    region   TEXT
);