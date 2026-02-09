import pandas as pd
from sqlalchemy import create_engine

def ingest_public_data(file_path: str, db_url: str):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.lower().str.strip()
    df['date'] = pd.to_datetime(df['date'])

    engine = create_engine(db_url)
    df.to_sql('raw_public_data', engine, if_exists='replace', index=False)
    print(f"✅ Loaded {len(df)} rows into table 'raw_public_data'")

if __name__ == "__main__":
    import os
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    file_path = os.getenv("PUBLIC_DATA_PATH", os.path.join(_root, "data", "DailyDelhiClimateTrain.csv"))
    db_url = os.getenv("DB_URL", "postgresql://postgres:changeme@localhost:5432/MyDB")
    ingest_public_data(file_path, db_url)
