import requests
import pandas as pd
from sqlalchemy import create_engine


def ingest_fake_api_data(api_url: str, db_url: str):
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "records" not in data:
        raise ValueError("API response missing 'records' key")
    records = data["records"]

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])

    engine = create_engine(db_url)
    df.to_sql("raw_fake_data", engine, if_exists="replace", index=False)
    print(f"✅ Loaded {len(df)} fake rows into table 'raw_fake_data'")

if __name__ == "__main__":
    import os
    api_url = os.getenv("API_URL", "http://localhost:8000/fake_weather?days=30")
    db_url = os.getenv("DB_URL", "postgresql://postgres:changeme@localhost:5432/MyDB")
    ingest_fake_api_data(api_url, db_url)

