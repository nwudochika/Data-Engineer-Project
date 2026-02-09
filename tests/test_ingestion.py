"""Tests for ingestion module."""
import os
import sys
import pandas as pd
import pytest

# Project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.ingest_public_data import ingest_public_data
from sqlalchemy import create_engine, text


def test_ingest_public_data_creates_table_and_rows(tmp_path):
    """Ingest public CSV into SQLite; verify table and row count."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "DailyDelhiClimateTrain.csv")
    if not os.path.isfile(csv_path):
        pytest.skip("Public CSV not found")
    db_path = tmp_path / "test.db"
    db_url = f"sqlite:///{db_path}"
    ingest_public_data(csv_path, db_url)
    engine = create_engine(db_url)
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM raw_public_data"), conn)
    assert len(df) > 0
    assert "date" in df.columns
    assert "meantemp" in [c.lower() for c in df.columns] or "mean_temp" in [c.lower() for c in df.columns]


def test_ingest_fake_api_validates_response(monkeypatch):
    """API ingestion should require 'records' in JSON."""
    import ingestion.ingest_fake_api as m
    class FakeResponse:
        def raise_for_status(self): pass
        def json(self): return {"count": 0}  # no "records" key
    def fake_get(*args, **kwargs): return FakeResponse()
    monkeypatch.setattr("ingestion.ingest_fake_api.requests.get", fake_get)
    with pytest.raises(ValueError, match="records"):
        m.ingest_fake_api_data("http://localhost:8000/fake_weather?days=1", "sqlite:///:memory:")
