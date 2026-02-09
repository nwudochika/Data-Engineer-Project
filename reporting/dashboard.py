import os
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", "postgresql://postgres:Plan10boy%26@localhost:5432/MyDB")


def run_dashboard():
    engine = create_engine(DB_URL)
    # dbt may create the view in public_public or public depending on config
    for table in ("public_public.curated_weather", "public.curated_weather", "curated_weather"):
        try:
            df = pd.read_sql(text(f"SELECT * FROM {table} ORDER BY date"), engine)
            break
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(type(e).__name__):
                continue
            raise
    else:
        raise RuntimeError(
            "curated_weather view not found. Run the pipeline first: docker compose up"
        )
    fig = px.line(
        df, x="date", y="mean_temp", color="source",
        title="Weather Trends (Public vs Fake)"
    )
    fig.show()


if __name__ == "__main__":
    run_dashboard()

