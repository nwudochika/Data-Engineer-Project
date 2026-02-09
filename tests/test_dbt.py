"""Smoke tests for dbt project."""
import os
import shutil
import subprocess
import pytest


def test_dbt_compile():
    """dbt compile should succeed (no DB required)."""
    if not shutil.which("dbt"):
        pytest.skip("dbt not in PATH")
    dbt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dbt"))
    env = os.environ.copy()
    env["DBT_PROFILES_DIR"] = dbt_dir
    env["DB_HOST"] = "localhost"
    env["DB_PORT"] = "5432"
    env["DB_USER"] = "postgres"
    env["DB_PASSWORD"] = "x"
    env["DB_NAME"] = "MyDB"
    r = subprocess.run(
        ["dbt", "compile"],
        cwd=dbt_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, (r.stdout or "") + (r.stderr or "")
