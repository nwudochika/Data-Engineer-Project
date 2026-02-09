# Technical Decisions and Rationale

## 1. Orchestration: Python script instead of Airflow/Prefect

**Decision**: Use a single Python orchestrator (`pipeline/orchestrator.py`) that runs ingestion then `dbt run` in process.

**Rationale**: The pipeline is linear (ingest → transform → done) and runs once per invocation. A lightweight script keeps the repo simple and avoids extra infrastructure. The same script works locally and in Docker. For production at scale, we could replace it with Airflow/Prefect DAGs that call the same ingestion and dbt steps.

---

## 2. Transformation: dbt for curation

**Decision**: All transformation and curation (rounding, union, `source` column) live in dbt models; no ad-hoc SQL in the repo.

**Rationale**: dbt gives versioned, testable SQL and a clear lineage (sources → staging → curated). The orchestrator only runs `dbt run`; no duplicate logic. Staging and curated models are in the `dbt/` folder with sources defined in `sources.yml`.

---

## 3. Raw table replacement and view dependencies

**Decision**: Before each run, the orchestrator drops the dbt-created views (`public_public.*`) so that pandas `to_sql(..., if_exists="replace")` can replace the raw tables without "dependent objects" errors.

**Rationale**: Postgres does not allow dropping a table that views depend on. Re-running the pipeline would fail when ingestion tried to replace `raw_fake_data` / `raw_public_data`. Dropping views first (then re-creating them via dbt run) keeps re-runs idempotent.

---

## 4. dbt schema: `public_public`

**Decision**: Accept that dbt creates objects in schema `public_public` (due to profile schema + custom schema both being "public").

**Rationale**: Changing this would require custom dbt macros or profile tweaks. The dashboard and orchestrator explicitly reference `public_public.curated_weather` where needed. Documented in README and docs.

---

## 5. Config via environment variables

**Decision**: Database and API connection details come from env vars (`DB_HOST`, `DB_USER`, `API_HOST`, etc.); `.env.example` documents them; no secrets in repo.

**Rationale**: Same code runs locally and in Docker by changing env (e.g. `DB_HOST=db` in Docker). Keeps credentials out of the codebase and supports `.env` in `.gitignore`.

---

## 6. Wait-for-services before pipeline

**Decision**: When `WAIT_FOR_SERVICES=1` (default), the orchestrator polls the database and FastAPI until both respond before running ingestion.

**Rationale**: With `docker compose up`, the pipeline container starts with db and fastapi_app; the API may not be ready immediately. Waiting avoids transient failures and keeps a single-command run reliable.

---

## 7. Reporting: Plotly dashboard

**Decision**: One reporting script (`reporting/dashboard.py`) that reads `curated_weather` (trying `public_public` then `public`) and opens a Plotly line chart.

**Rationale**: Meets "relevant reporting applicant's choice" with minimal dependencies. The script is optional and run via `make report` after the pipeline has populated the curated view.
