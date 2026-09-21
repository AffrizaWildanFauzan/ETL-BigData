import pandas as pd
import logging

logger = logging.getLogger(__name__)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transformasi dataset Urban Traffic Congestion and Travel Time Analysis.

    Kolom asli dataset:
        - record_id             : ID unik tiap observasi
        - date_time             : Waktu observasi
        - city_zone             : Zona kota (Residential, Industrial, Commercial)
        - road_type             : Jenis jalan (Highway, Main Road, Local Road)
        - traffic_volume        : Volume kendaraan (50–2999)
        - average_speed_kmh     : Kecepatan rata-rata (10.1–80 km/jam)
        - weather_condition     : Cuaca (Clear, Rain, Storm, Fog, Cloudy)
        - accident_reported     : Apakah ada kecelakaan (true/false)
        - travel_time_minutes   : Estimasi waktu tempuh (5–120 menit)
        - congestion_level      : Tingkat kemacetan (Low, Medium, High)

    Transformasi yang dilakukan:
        1. Konversi date_time ke datetime
        2. Feature engineering dari date_time (year, month, day, hour, dll)
        3. Konversi kolom numerik
        4. Konversi accident_reported ke boolean
        5. Bersihkan kolom kategorikal (strip, uppercase missing)
        6. Filter data invalid (volume/speed/travel time <= 0)
        7. Drop duplikat

    Args:
        df (pd.DataFrame): DataFrame mentah dari extract.

    Returns:
        pd.DataFrame: DataFrame bersih siap load.
    """
    logger.info("[TRANSFORM] Mulai proses transformasi")
    initial_rows = len(df)

    # ============================================================
    # 1. Konversi kolom tanggal
    # ============================================================
    if 'date_time' in df.columns:
        df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')
        df = df.dropna(subset=['date_time'])
        logger.info(f"[TRANSFORM] Setelah drop date_time invalid: {len(df)} baris")

        # ========================================================
        # 2. Feature engineering dari date_time
        # ========================================================
        df['year'] = df['date_time'].dt.year
        df['month'] = df['date_time'].dt.month
        df['day'] = df['date_time'].dt.day
        df['hour'] = df['date_time'].dt.hour
        df['day_of_week'] = df['date_time'].dt.dayofweek      # 0=Senin, 6=Minggu
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        df['is_peak_hour'] = df['hour'].isin([7, 8, 9, 17, 18, 19])

    # ============================================================
    # 3. Konversi kolom numerik
    # ============================================================
    numeric_cols = ['traffic_volume', 'average_speed_kmh', 'travel_time_minutes']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # ============================================================
    # 4. Konversi accident_reported ke boolean
    # ============================================================
    if 'accident_reported' in df.columns:
        # Handle berbagai format: true/false, True/False, 1/0, yes/no
        if df['accident_reported'].dtype == 'object':
            df['accident_reported'] = (
                df['accident_reported']
                .astype(str)
                .str.strip()
                .str.lower()
                .map({'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False})
            )
        df['accident_reported'] = df['accident_reported'].fillna(False).astype(bool)

    # ============================================================
    # 5. Bersihkan kolom kategorikal
    # ============================================================
    categorical_cols = ['city_zone', 'road_type', 'weather_condition', 'congestion_level']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna('UNKNOWN').astype(str).str.strip()

    # ============================================================
    # 6. Filter data invalid
    # ============================================================
    if 'traffic_volume' in df.columns:
        df = df[df['traffic_volume'] > 0]
    if 'average_speed_kmh' in df.columns:
        df = df[df['average_speed_kmh'] > 0]
    if 'travel_time_minutes' in df.columns:
        df = df[df['travel_time_minutes'] > 0]

    logger.info(f"[TRANSFORM] Setelah filter invalid: {len(df)} baris")

    # ============================================================
    # 7. Drop duplikat
    # ============================================================
    df = df.drop_duplicates()

    # ============================================================
    # 8. Reset index
    # ============================================================
    df = df.reset_index(drop=True)

    logger.info(f"[TRANSFORM] Selesai. {initial_rows} → {len(df)} baris")
    return df