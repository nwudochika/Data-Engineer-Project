"""
Orchestrator: runs Python ingestion then dbt to produce the curated dataset.
Matches the infrastructure: Container = Database + dbt + Orchestrator + Python Ingestion.
"""
import os
import sys
import subprocess
import time
import pandas as pd
import requests
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ingestion.ingest_public_data import ingest_public_data
from ingestion.ingest_fake_api import ingest_fake_api_data

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DBT_DIR = os.path.join(_PROJECT_ROOT, "dbt")

# Wait settings (for docker compose up – pipeline runs after API/DB are ready)
_WAIT_TIMEOUT_SEC = int(os.environ.get("WAIT_TIMEOUT_SEC", "120"))
_WAIT_INTERVAL_SEC = float(os.environ.get("WAIT_INTERVAL_SEC", "3"))


def _get_config():
    """Config from env (Docker) with defaults for local run."""
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "changeme")
    db_name = os.environ.get("DB_NAME", "MyDB")
    # URL-encode password if needed (e.g. & -> %26)
    from urllib.parse import quote_plus
    db_url = f"postgresql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"

    api_host = os.environ.get("API_HOST", "localhost")
    api_port = os.environ.get("API_PORT", "8000")
    api_url = os.environ.get("API_URL") or f"http://{api_host}:{api_port}/fake_weather?days=30"

    file_path = os.environ.get("PUBLIC_DATA_PATH") or os.path.join(
        _PROJECT_ROOT, "data", "DailyDelhiClimateTrain.csv"
    )
    return {
        "db_url": db_url,
        "api_url": api_url,
        "file_path": file_path,
        "db_host": db_host,
        "db_port": db_port,
        "db_user": db_user,
        "db_password": db_password,
        "db_name": db_name,
        "api_host": api_host,
        "api_port": api_port,
    }


def _wait_for_services(config):
    """Wait for DB and FastAPI to be ready (used when running via docker compose up)."""
    db_url = config["db_url"]
    api_check = f"http://{config['api_host']}:{config['api_port']}/"

    deadline = time.monotonic() + _WAIT_TIMEOUT_SEC
    print("Waiting for Database and FastAPI to be ready...")
    while time.monotonic() < deadline:
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False
        try:
            r = requests.get(api_check, timeout=5)
            api_ok = r.status_code == 200
        except Exception:
            api_ok = False
        if db_ok and api_ok:
            print("Database and FastAPI are ready.")
            return
        time.sleep(_WAIT_INTERVAL_SEC)
    raise RuntimeError(
        "Timeout waiting for Database and/or FastAPI. "
        f"Check that db and fastapi_app are running (timeout={_WAIT_TIMEOUT_SEC}s)."
    )


def main_pipeline():
    config = _get_config()
    db_url = config["db_url"]
    api_url = config["api_url"]
    file_path = config["file_path"]

    print("Starting Weather Pipeline (Orchestrator)")

    # Wait for DB and API when running in Docker (e.g. docker compose up)
    if os.environ.get("WAIT_FOR_SERVICES", "1") == "1":
        _wait_for_services(config)

    # Drop dbt views from any previous run so we can replace raw tables
    engine = create_engine(db_url)
    with engine.connect() as conn:
        for view in ("public_public.curated_weather", "public_public.stg_fake_data", "public_public.stg_public_data"):
            conn.execute(text(f"DROP VIEW IF EXISTS {view} CASCADE"))
        conn.commit()

    # Step 1: Python Ingestion – public dataset
    ingest_public_data(file_path, db_url)

    # Step 2: Python Ingestion – FastAPI fake dataset
    ingest_fake_api_data(api_url, db_url)

    # Step 3: dbt – curated and cleaned dataset
    env = os.environ.copy()
    env["DB_HOST"] = config["db_host"]
    env["DB_PORT"] = config["db_port"]
    env["DB_USER"] = config["db_user"]
    env["DB_PASSWORD"] = config["db_password"]
    env["DB_NAME"] = config["db_name"]
    env["DBT_PROFILES_DIR"] = _DBT_DIR
    result = subprocess.run(
        ["dbt", "run"],
        cwd=_DBT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        raise RuntimeError("dbt run failed")
    print("dbt run completed.")

    # Step 4: Verify (dbt creates the view in public_public)
    engine = create_engine(db_url)
    df = pd.read_sql(text("SELECT COUNT(*) AS total_records FROM public_public.curated_weather"), engine)
    total = int(df["total_records"].iloc[0])
    print(f"Curated dataset has {total} rows.")
    print("Pipeline completed successfully!")


if __name__ == "__main__":
    main_pipeline()
