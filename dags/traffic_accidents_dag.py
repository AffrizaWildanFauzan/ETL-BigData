from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import sys
import os

# Tambahkan root project ke sys.path agar bisa import `etl`
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_to_file, load_to_database

# Konfigurasi path (di dalam container Airflow)
RAW_PATH = "/opt/airflow/data/raw/traffic_accidents.csv"
CLEAN_PARQUET_PATH = "/opt/airflow/data/clean/traffic_accidents_clean.parquet"
DB_URL = "postgresql+psycopg2://airflow:airflow@traffic-meta-db:5432/airflow"
DB_TABLE = "traffic_accidents"

default_args = {
    'owner': 'traffic_etl',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# Wrapper fungsi untuk Airflow 

def task_extract(**context):
    df = extract_data(RAW_PATH)
    # Simpan ke parquet sementara, passing path via XCom
    tmp_path = "/opt/airflow/data/clean/_raw_tmp.parquet"
    df.to_parquet(tmp_path, index=False)
    context['ti'].xcom_push(key='raw_path', value=tmp_path)
    return tmp_path


def task_transform(**context):
    import pandas as pd
    raw_path = context['ti'].xcom_pull(task_ids='extract_data', key='raw_path')
    df = pd.read_parquet(raw_path)
    df_clean = transform_data(df)
    clean_path = "/opt/airflow/data/clean/_clean_tmp.parquet"
    df_clean.to_parquet(clean_path, index=False)
    context['ti'].xcom_push(key='clean_path', value=clean_path)
    return clean_path


def task_load(**context):
    import pandas as pd
    clean_path = context['ti'].xcom_pull(task_ids='transform_data', key='clean_path')
    df_clean = pd.read_parquet(clean_path)
    load_to_file(df_clean, CLEAN_PARQUET_PATH, fmt='parquet')
    load_to_database(df_clean, DB_URL, DB_TABLE)


# DAG Definition 

with DAG(
    dag_id='traffic_accidents_etl',
    default_args=default_args,
    description='ETL batch Traffic Accidents menggunakan Airflow',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['traffic', 'etl', 'batch'],
    template_searchpath=['/opt/airflow/sql']
) as dag:

    create_table = PostgresOperator(
        task_id='create_traffic_table',
        postgres_conn_id='postgres_traffic',
        sql='create_traffic_table.sql',
    )

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=task_extract,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=task_transform,
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=task_load,
    )

    create_table >> extract_task >> transform_task >> load_task