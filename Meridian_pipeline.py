import pandas as pd
from dotenv import load_dotenv
import os
import requests
from sqlalchemy import create_engine
import psycopg2
from datetime import datetime
import logging #help to track what is going on in the pipeline
import gspread
from psycopg2.extras import execute_values


 ###--- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("extract.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Config ---
GOOGLE_API_KEY = "AIzaSyBPrFVVjWXgOhdWgnsjkeS3icH1ZBjy93U"

SHEET_TABLE_MAP = [
    {
        "spreadsheet_id": "1oDXxaZLD2KP1U4bfxtY9YiipIaA2FABDL19adSCw2rk",
        "sheet_name":     "MeridianMart_Products_Master",
        "table":          "raw.products"
    },
    {
        "spreadsheet_id": "1shTuXYx7jrUOi6aXWDHfFwTI_1sQCGuIAngOk_UxpkM",
        "sheet_name":     "MeridianMart_Managers_Master",
        "table":          "raw.managers"
    },
    {
        "spreadsheet_id": "1VLadzdv5sba3iFEg8Un2OkE_tlnFeNaHg2YxWvH8Az8",
        "sheet_name":     "MeridianMart_Stores_Master",
        "table":          "raw.stores"
    },
    {
        "spreadsheet_id": "1iR3ghJkSiEV11ZrVtcvCKbwRhke9HeictvA6f-sVEZ0",
        "sheet_name":     "MeridianMart_Staff_Master",
        "table":          "raw.staff"
    },
]

DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "MeridianMart_DB",
    "user":     "postgres",
    "password": "Matric2700"
}

# --- Extract from Google Sheets ---
def extract_sheet(client, spreadsheet_id, sheet_name):
    logger.info(f"Extracting sheet: {sheet_name}")
    ws = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    rows = ws.get_all_records()
    logger.info(f"  {len(rows)} rows fetched from {sheet_name}")
    return rows

# --- Load into PostgreSQL ---
def load_to_postgres(conn, table, rows):
    if not rows:
        logger.warning(f"  No rows to load for {table}, skipping.")
        return 0

    columns = list(rows[0].keys())
    values = [tuple(row[col] for col in columns) for row in rows]
    col_str = ", ".join(columns)

    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table};")
        logger.info(f"  Truncated {table}")

        insert_sql = f"INSERT INTO {table} ({col_str}) VALUES %s"
        execute_values(cur, insert_sql, values)
        conn.commit()

    logger.info(f"  {len(rows)} rows loaded into {table}")
    return len(rows)

# --- Main ---
def main():
    logger.info("=== Reference Sheet Extraction Started ===")

    # Authenticate with API 
    gc = gspread.api_key(GOOGLE_API_KEY)
    logger.info("Authenticated with Google Sheets API")

    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    logger.info("Connected to PostgreSQL")

    # Process each sheet
    for item in SHEET_TABLE_MAP:
        sheet_name = item["sheet_name"]
        table_name = item["table"]
        spreadsheet_id = item["spreadsheet_id"]

        try:
            rows = extract_sheet(gc, spreadsheet_id, sheet_name)
            count = load_to_postgres(conn, table_name, rows)

            with open("extract.log", "a") as log_file:
                log_file.write(
                    f"{datetime.now()} | {table_name} | {count} rows loaded\n"
                )

        except Exception as e:
            logger.error(f"Failed on {sheet_name}: {type(e).__name__}: {e}")
            conn.rollback()

    conn.close()
    logger.info("=== Extraction Complete ===")

if __name__ == "__main__":
        main()