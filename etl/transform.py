import pandas as pd
import logging

logger = logging.getLogger(__name__)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melakukan transformasi data Traffic Accidents:
    - Konversi tipe tanggal
    - Handling missing values
    - Feature engineering
    - Konversi tipe numerik
    - Drop duplikat

    Args:
        df (pd.DataFrame): DataFrame mentah.

    Returns:
        pd.DataFrame: DataFrame bersih.
    """
    logger.info("[TRANSFORM] Mulai proses transformasi")
    initial_rows = len(df)

    # 1. Konversi tanggal
    df['crash_date'] = pd.to_datetime(df['crash_date'], errors='coerce')
    df = df.dropna(subset=['crash_date'])
    logger.info(f"[TRANSFORM] Setelah drop tanggal invalid: {len(df)} baris")

    # 2. Feature engineering dari tanggal
    df['crash_year'] = df['crash_date'].dt.year
    df['crash_month'] = df['crash_date'].dt.month
    df['crash_dow'] = df['crash_date'].dt.dayofweek  # 0=Senin, 6=Minggu
    df['is_weekend'] = df['crash_dow'].isin([5, 6])

    # 3. Konversi kolom numerik
    numeric_cols = [
        'injuries_total', 'injuries_fatal', 'injuries_incapacitating',
        'injuries_non_incapacitating', 'injuries_reported_not_evident',
        'injuries_no_indication', 'num_units'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 4. Isi missing value pada kolom kategorikal
    categorical_cols = [
        'traffic_control_device', 'weather_condition', 'lighting_condition',
        'first_crash_type', 'trafficway_type', 'alignment',
        'roadway_surface_cond', 'road_defect', 'crash_type',
        'intersection_related_i', 'damage', 'prim_contributory_cause',
        'most_severe_injury'
    ]
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('UNKNOWN').astype(str).str.strip()

    # 5. Filter data invalid (misal injuries negatif)
    df = df[df['injuries_total'] >= 0]

    # 6. Drop duplikat
    df = df.drop_duplicates()

    logger.info(f"[TRANSFORM] Selesai. {initial_rows} → {len(df)} baris")
    return df.reset_index(drop=True)