import logging
import os
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_to_file, load_to_database

# ============================================================
# Konfigurasi Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# Konfigurasi Path
# ============================================================
RAW_PATH = "data/raw/urban_traffic_congestion_travel_time.csv"
CLEAN_PARQUET_PATH = "data/clean/urban_traffic_clean.parquet"
CLEAN_CSV_PATH = "data/clean/urban_traffic_clean.csv"

# ============================================================
# Konfigurasi Database (opsional)
# ============================================================
# Contoh: postgresql+psycopg2://airflow:airflow@localhost:5432/airflow
DB_URL = os.getenv("DB_URL", "")
DB_TABLE = "urban_traffic_congestion"


def run_etl():
    """
    Jalankan pipeline ETL lengkap:
        1. Extract dari CSV
        2. Transform
        3. Load ke file (Parquet + CSV)
        4. Load ke database (opsional)
    """
    logger.info("=" * 60)
    logger.info("ETL BATCH URBAN TRAFFIC CONGESTION - START")
    logger.info("=" * 60)

    # ============================================================
    # 1. EXTRACT
    # ============================================================
    df_raw = extract_data(RAW_PATH)

    # ============================================================
    # 2. TRANSFORM
    # ============================================================
    df_clean = transform_data(df_raw)

    # ============================================================
    # 3. LOAD — ke file
    # ============================================================
    load_to_file(df_clean, CLEAN_PARQUET_PATH, fmt='parquet')
    load_to_file(df_clean, CLEAN_CSV_PATH, fmt='csv')

    # ============================================================
    # 4. LOAD — ke database (opsional)
    # ============================================================
    if DB_URL:
        load_to_database(df_clean, DB_URL, DB_TABLE)
    else:
        logger.info("[LOAD] DB_URL tidak diset, skip load ke database")

    logger.info("=" * 60)
    logger.info("ETL BATCH URBAN TRAFFIC CONGESTION - FINISHED")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_etl()