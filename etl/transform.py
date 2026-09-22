import logging
import pandas as pd

logger = logging.getLogger(__name__)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
  """Transformasi dataset Urban Traffic Congestion and Travel Time Analysis.

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
      1. CLEANING          : Pembersihan numerik, kategorikal, boolean,
      filter invalid, & drop duplicate
      2. CONVERT DATE_TIME : Konversi date_time ke datetime & drop invalid
      3. FEATURE ENG.      : Ekstraksi hour_of_day, day_of_week, is_peak_hour,
      & congestion_index

  Args:
      df (pd.DataFrame): DataFrame mentah dari extract.

  Returns:
      pd.DataFrame: DataFrame bersih siap load.
  """
  logger.info("[TRANSFORM] Mulai proses transformasi")
  initial_rows = len(df)

  # 1. CLEANING
  # a. Konversi & pembersihan kolom numerik
  numeric_cols = [
      "traffic_volume",
      "average_speed_kmph",
      "travel_time_minutes",
  ]
  for col in numeric_cols:
    if col in df.columns:
      df[col] = pd.to_numeric(df[col], errors="coerce")

  # b. Konversi accident_reported ke boolean
  if "accident_reported" in df.columns:
    if df["accident_reported"].dtype == "object":
      df["accident_reported"] = (
          df["accident_reported"]
          .astype(str)
          .str.strip()
          .str.lower()
          .map({
              "true": True,
              "false": False,
              "yes": True,
              "no": False,
              "1": True,
              "0": False,
          })
      )
    df["accident_reported"] = df["accident_reported"].fillna(False).astype(bool)

  # c. Bersihkan kolom kategorikal
  categorical_cols = [
      "city_zone",
      "road_type",
      "weather_condition",
      "congestion_level",
  ]
  for col in categorical_cols:
    if col in df.columns:
      df[col] = df[col].fillna("UNKNOWN").astype(str).str.strip()

  # d. Filter data invalid (volume / speed / travel time <= 0)
  if "traffic_volume" in df.columns:
    df = df[df["traffic_volume"] > 0]
  if "average_speed_kmph" in df.columns:
    df = df[df["average_speed_kmph"] > 0]
  if "travel_time_minutes" in df.columns:
    df = df[df["travel_time_minutes"] > 0]

  # e. Drop duplikat
  df = df.drop_duplicates()
  logger.info(f"[TRANSFORM] Setelah cleaning data: {len(df)} baris")

  
  # 2. CONVERT DATE_TIME
  if "date_time" in df.columns:
    df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
    df = df.dropna(subset=["date_time"])
    logger.info(
        f"[TRANSFORM] Setelah convert & drop date_time invalid: {len(df)} baris"
    )

    
    # 3. FEATURE ENGINEERING
    # a. hour_of_day: Ekstraksi jam (0 - 23)
    df["hour_of_day"] = df["date_time"].dt.hour

    # b. day_of_week: Nama hari (Monday, Tuesday, dll)
    df["day_of_week"] = df["date_time"].dt.day_name()

    # c. is_peak_hour: Indikator jam sibuk (07.00–09.00 & 17.00–19.00)
    df["is_peak_hour"] = df["hour_of_day"].isin([7, 8, 9, 17, 18, 19])

    # d. congestion_index: Rasio Kepadatan Traffic (Volume / Speed)
    if (
        "traffic_volume" in df.columns
        and "average_speed_kmph" in df.columns
    ):
      df["congestion_index"] = (
          df["traffic_volume"] / df["average_speed_kmph"]
      ).round(2)


  # 4. RESET INDEX & FINALIZE
  df = df.reset_index(drop=True)

  logger.info(f"[TRANSFORM] Selesai. {initial_rows} → {len(df)} baris")
  return df
