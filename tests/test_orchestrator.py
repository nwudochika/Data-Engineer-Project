"""Tests for pipeline orchestrator config."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.orchestrator import _get_config


def test_get_config_returns_required_keys():
    """Orchestrator config must include db_url, api_url, file_path and DB vars."""
    config = _get_config()
    assert "db_url" in config
    assert "api_url" in config
    assert "file_path" in config
    assert "db_host" in config
    assert "db_name" in config


def test_get_config_db_url_is_postgres_like():
    config = _get_config()
    assert config["db_url"].startswith("postgresql://")
