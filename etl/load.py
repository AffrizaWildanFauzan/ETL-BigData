import pandas as pd
import logging
import os
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


def load_to_file(df: pd.DataFrame, output_path: str, fmt: str = 'parquet') -> None:
    """
    Simpan DataFrame ke file (parquet/csv).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    logger.info(f"[LOAD] Menyimpan data ke {output_path} (format={fmt})")
    if fmt == 'parquet':
        df.to_parquet(output_path, index=False)
    elif fmt == 'csv':
        df.to_csv(output_path, index=False)
    else:
        raise ValueError(f"Format tidak didukung: {fmt}")
    logger.info(f"[LOAD] Berhasil menyimpan {len(df)} baris")


def load_to_database(df: pd.DataFrame, db_url: str, table_name: str) -> None:
    """
    Load DataFrame ke tabel database (PostgreSQL/MySQL/SQLite).
    """
    logger.info(f"[LOAD] Menulis ke database: {table_name}")
    engine = create_engine(db_url)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    logger.info(f"[LOAD] Berhasil menulis {len(df)} baris ke tabel {table_name}")