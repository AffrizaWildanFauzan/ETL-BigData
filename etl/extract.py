import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)


def extract_data(file_path: str) -> pd.DataFrame:
    """
    Membaca dataset mentah Traffic Accidents dari file CSV.

    Args:
        file_path (str): Path ke file CSV mentah.

    Returns:
        pd.DataFrame: DataFrame hasil ekstraksi.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

    logger.info(f"[EXTRACT] Membaca file: {file_path}")
    df = pd.read_csv(file_path, low_memory=False)
    logger.info(f"[EXTRACT] Berhasil membaca {len(df)} baris, {len(df.columns)} kolom")

    return df