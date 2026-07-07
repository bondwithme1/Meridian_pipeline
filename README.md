A production-style data engineering pipeline that extracts sales and reference data from Google Sheets into a PostgreSQL data warehouse.

## Tech Stack
- Python 3.13
- PostgreSQL 18
- gspread (Google Sheets API)
- psycopg2
- GitHub Actions (CI/CD)

## Architecture
Google Sheets (15 sheets) → Python Extraction Scripts → PostgreSQL (Raw → Staging)

## Project Structure
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
...and so on
```