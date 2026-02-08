import subprocess
import pandas as pd
from sqlalchemy import create_engine
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ingestion.ingest_public_data import ingest_public_data
from ingestion.ingest_fake_api import ingest_fake_api_data


def main_pipeline():
    db_url = "postgresql://postgres:Plan10boy%26@localhost:5432/MyDB"
    api_url = "http://localhost:8000/fake_weather?days=30"
    file_path = "data/DailyDelhiClimateTrain.csv"

    print("Starting Weather Pipeline")

    # Step 1: Load public dataset
    ingest_public_data(file_path, db_url)

    # Step 2: Ingest fake dataset
    ingest_fake_api_data(api_url, db_url)

    # Step 3: Apply SQL transformation
    engine = create_engine(db_url)
    with engine.connect() as conn:
        conn.execute(open("transformations/curated_weather.sql", "r").read())
        conn.commit()

    # Step 4: Verify
    df = pd.read_sql("SELECT COUNT(*) AS total_records FROM curated_weather", engine)
    print(f"Combined dataset now has {df.total_records.iloc[0]} rows")
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    main_pipeline()
