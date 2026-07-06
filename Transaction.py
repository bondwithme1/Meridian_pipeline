import logging
import gspread
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("extract.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Google API Key ---
GOOGLE_API_KEY = "AIzaSyBPrFVVjWXgOhdWgnsjkeS3icH1ZBjy93U"

# --- 11 Store Sheets Config ---
STORE_CONFIG = [
    {"store_id": "S001", "spreadsheet_id": "1dob3p4TRkWj-jN3imsNcihFSajZ_9u4ZkEKWdBVrDV8",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S001_June1-15"},
    {"store_id": "S002", "spreadsheet_id": "1hEb2KZZlqD_cyRfSF8KDiPCAcQ8Igqr89ooJ2yfqstg",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S002_June1-15"},
    {"store_id": "S003", "spreadsheet_id": "1NkNRsHkMO8jg5BCG0igHYdorFqKx-APmoRR5K15muDo",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S003_June1-15"},
    {"store_id": "S004", "spreadsheet_id": "1iAgxk_XP8rZBXxHa6zH7YZQno3vVqaEVD8vpHuqB-2U",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S004_June1-15"},
    {"store_id": "S005", "spreadsheet_id": "1R04N8FmX3KeMdKb9-cSZDgluBq2N4Q8_WNAsXOXbGlc",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S005_June1-15"},
    {"store_id": "S006", "spreadsheet_id": "1q5_-lY_trscnJOwiFWedyOOPC2agq0vnqnXVTc9IgG0",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S006_June1-15"},
    {"store_id": "S007", "spreadsheet_id": "1imTaeiPNKWO2jLg5YBjny6UlcXnlFqkHcNKvj0cDBJ4",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S007_June1-15"},
    {"store_id": "S008", "spreadsheet_id": "1OXcsRtjx7GSbtVmvDZr-KogCVXsEhe_AkUoF9wOyngw",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S008_June1-15"},
    {"store_id": "S009", "spreadsheet_id": "1sXTnfqBRcg1u_-DRyn_-yWZdIGG96E_mQoHsiHJz6FA",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S009_June1-15"},
    {"store_id": "S010", "spreadsheet_id": "1CHfGZ6-D_meZj3t5y3KIWu3qvD9vNTWdS24udz23zmE",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S010_June1-15"},
    {"store_id": "S011", "spreadsheet_id": "10u8ny3KHNSQ1SCSCwEjdmFiULhPcrn5wSnK-RVB6REM",
        "sheet_name": "MeridianMart_GoogleForm_SalesLog_S011_June1-15"},
]

# --- DB Config ---
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "MeridianMart_DB",
    "user":     "postgres",
    "password": "Matric2700"
}

# --- Canonical column names ---
CANONICAL_COLUMNS = [
    "timestamp",
    "store_id",
    "staff_name",
    "receipt_no",
    "customer_phone_number_optional",
    "product_sold",
    "quantity",
    "payment_method",
    "source_sheet"
]

# --- Normalise headers ---


def normalise_headers(rows, store_id, sheet_name):
    normalised = []
    for row in rows:
        clean = {}
        for k, v in row.items():
            key = k.strip().lower().replace(" ", "_").replace(
                ".", "").replace("(", "").replace(")", "")
            # Convert all values to string, handle empty
            clean[key] = str(v) if v != "" else ""
        clean["store_id"] = store_id
        clean["source_sheet"] = sheet_name
        normalised.append(clean)
    return normalised
# --- Extract from Google Sheets ---


def extract_sheet(client, spreadsheet_id, sheet_name):
    logger.info(f"Extracting sheet: {sheet_name}")
    ws = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    rows = ws.get_all_records()
    logger.info(f"  {len(rows)} rows fetched from {sheet_name}")
    return rows

# --- Load into raw.transactions ---


def load_to_postgres(conn, rows):
    if not rows:
        logger.warning("  No rows to load, skipping.")
        return 0

    values = [
        tuple(row.get(col, "") for col in CANONICAL_COLUMNS)
        for row in rows
    ]

    insert_sql = f"""
        INSERT INTO raw.transactions ({", ".join(CANONICAL_COLUMNS)})
        VALUES %s
    """

    with conn.cursor() as cur:
        execute_values(cur, insert_sql, values)
        conn.commit()

    logger.info(f"  {len(rows)} rows inserted into raw.transactions")
    return len(rows)

# --- Main ---


def main():
    logger.info("=== Store Sheet Extraction Started ===")

    gc = gspread.api_key(GOOGLE_API_KEY)
    logger.info("Authenticated with Google Sheets API")

    conn = psycopg2.connect(**DB_CONFIG)
    logger.info("Connected to PostgreSQL")

    # Truncate once before loading all stores
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE raw.transactions;")
        conn.commit()
    logger.info("Truncated raw.transactions")

    total = 0
    for store in STORE_CONFIG:
        try:
            rows = extract_sheet(
                gc, store["spreadsheet_id"], store["sheet_name"])
            normalised = normalise_headers(
                rows, store["store_id"], store["sheet_name"])
            count = load_to_postgres(conn, normalised)
            total += count
        except Exception as e:
            logger.error(
                f"Failed on {store['store_id']}: {type(e).__name__}: {e}")
            conn.rollback()

    conn.close()
    logger.info(f"=== Extraction Complete: {total} total rows loaded ===")


if __name__ == "__main__":
    main()
