A production-style data engineering pipeline that extracts sales and reference data from Google Sheets into a PostgreSQL data warehouse.

## Tech Stack
- Python 3.13
- PostgreSQL 18
- gspread (Google Sheets API)
- psycopg2

## Architecture
Google Sheets (15 sheets) → Python Extraction Scripts → PostgreSQL (Raw → Staging)

## Project Structure
## Architecture
## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   DATA SOURCES                       │
│                                                      │
│  Google Sheets (15 sheets)                          │
│  ├── 11 Store SalesLog sheets (S001-S011)           │
│  └── 4 Reference sheets                             │
│      ├── Products Master                            │
│      ├── Staff Master                               │
│      ├── Managers Master                            │
│      └── Stores Master                              │
└─────────────────┬───────────────────────────────────┘
                  │ gspread API
                  ▼
┌─────────────────────────────────────────────────────┐
│               EXTRACTION LAYER                       │
│                                                      │
│  Python Scripts                                     │
│  ├── extract_references.py                          │
│  │   └── reads 4 reference sheets                  │
│  └── extract_transactions.py                        │
│      └── reads 11 store sheets                      │
│          └── normalise_headers()                    │
│          └── injects store_id + source_sheet        │
└─────────────────┬───────────────────────────────────┘
                  │ psycopg2
                  ▼
┌─────────────────────────────────────────────────────┐
│            RAW SCHEMA (PostgreSQL)                   │
│            Everything stored as TEXT                 │
│                                                      │
│  raw.transactions   (45,000+ rows)                  │
│  raw.products                                       │
│  raw.staff                                          │
│  raw.managers                                       │
│  raw.stores                                         │
└─────────────────┬───────────────────────────────────┘
                  │ type casting + validation
                  ▼
┌─────────────────────────────────────────────────────┐
│           STAGING SCHEMA (PostgreSQL)                │
│         Typed columns + Constraints                  │
│                                                      │
│  staging.transactions                               │
│  ├── quantity INTEGER CHECK (1-20)                  │
│  ├── payment_method CHECK (Cash/Card/Transfer)      │
│  └── NOT NULL on key fields                         │
│                                                      │
│  staging.products                                   │
│  staging.staff                                      │
│  staging.managers                                   │
│  staging.stores                                     │
└─────────────────┬───────────────────────────────────┘
                  │ invalid rows captured
                  ▼
┌─────────────────────────────────────────────────────┐
│              AUDIT SCHEMA (PostgreSQL)               │
│                                                      │
│  audit.validation_log                               │
│  ├── check_name                                     │
│  ├── store_id                                       │
│  ├── raw_value                                      │
│  └── flagged_at                                     │
└─────────────────────────────────────────────────────┘
```