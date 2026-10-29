"""
Accor Live Limitless (ALL) Loyalty Platform - Database Loader & SQL Analytics Runner
Loads raw data into SQLite database and executes the analytical SQL transformations.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "data/accor_loyalty.db"
SCHEMA_PATH = "sql/schema.sql"
RFM_QUERY_PATH = "sql/rfm_and_features.sql"
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"


def load_database(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Initialize database schema and populate with raw CSV data.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"[*] Reading and applying schema DDL from {SCHEMA_PATH}...")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("[+] Database schema successfully created.")
    
    # Load raw CSVs into tables
    table_files = [
        ("properties", os.path.join(RAW_DIR, "properties.csv")),
        ("loyalty_members", os.path.join(RAW_DIR, "loyalty_members.csv")),
        ("bookings", os.path.join(RAW_DIR, "bookings.csv")),
        ("campaign_interactions", os.path.join(RAW_DIR, "campaign_interactions.csv")),
    ]
    
    for table_name, csv_path in table_files:
        if os.path.exists(csv_path):
            print(f"[*] Loading {csv_path} into SQL table '{table_name}'...")
            df = pd.read_csv(csv_path)
            # Replace existing records if rerun
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"[+] Loaded {len(df)} records into '{table_name}'.")
        else:
            print(f"[!] Warning: {csv_path} does not exist.")
            
    conn.commit()
    return conn


def execute_rfm_sql_analytics(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Execute the complex analytical RFM SQL query on the database
    and extract enriched member metrics.
    """
    print(f"[*] Executing SQL Analytical Transformations from {RFM_QUERY_PATH}...")
    with open(RFM_QUERY_PATH, "r", encoding="utf-8") as f:
        rfm_query = f.read()
        
    df_rfm = pd.read_sql_query(rfm_query, conn)
    output_path = os.path.join(PROCESSED_DIR, "member_rfm_features.csv")
    df_rfm.to_csv(output_path, index=False)
    print(f"[OK] Analytical SQL transformation complete. Extracted {len(df_rfm)} member records.")
    print(f"[OK] Saved enriched RFM & churn features to {output_path}")
    return df_rfm


if __name__ == "__main__":
    conn = load_database()
    df_features = execute_rfm_sql_analytics(conn)
    conn.close()
