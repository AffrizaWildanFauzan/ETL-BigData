import logging
import os
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_to_file, load_to_database

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konfigurasi path
RAW_PATH = "data/raw/traffic_accidents.csv"
CLEAN_PARQUET_PATH = "data/clean/traffic_accidents_clean.parquet"
CLEAN_CSV_PATH = "data/clean/traffic_accidents_clean.csv"

# Konfigurasi database (opsional)
DB_URL = os.getenv("DB_URL", "")  # contoh: postgresql+psycopg2://airflow:airflow@localhost:5432/airflow
DB_TABLE = "traffic_accidents"


def run_etl():
    logger.info("=" * 60)
    logger.info("ETL BATCH TRAFFIC ACCIDENTS - START")
    logger.info("=" * 60)

    # Extract
    df_raw = extract_data(RAW_PATH)

    # Transform
    df_clean = transform_data(df_raw)

    # Load ke file
    load_to_file(df_clean, CLEAN_PARQUET_PATH, fmt='parquet')
    load_to_file(df_clean, CLEAN_CSV_PATH, fmt='csv')

    # Load ke database (opsional, hanya jika DB_URL diset)
    if DB_URL:
        load_to_database(df_clean, DB_URL, DB_TABLE)
    else:
        logger.info("[LOAD] DB_URL tidak diset, skip load ke database")

    logger.info("=" * 60)
    logger.info("ETL BATCH TRAFFIC ACCIDENTS - FINISHED")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_etl()