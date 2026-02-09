# Data-Engineer-Project

This repository implements the data pipeline and infrastructure described below.

## Infrastructure (high level)

- **Code repository**: This repo contains all components.
- **Data sources**:
  - **Public dataset** (e.g. Daily Delhi Climate) — provided as CSV; ingested into the database.
  - **FastAPI fake dataset** — applicant-created; a FastAPI app generates synthetic weather data and the pipeline ingests it.
- **Container** (Docker Compose) runs:
  - **Database** (PostgreSQL): stores raw and curated data.
  - **dbt**: builds the curated, cleaned dataset from raw tables.
  - **Orchestrator**: runs the pipeline (Python ingestion → dbt).
  - **Python ingestion**: loads the public CSV and the FastAPI fake data into the database.
- **Output**: A **curated and cleaned dataset** (view `curated_weather`) used for reporting.
- **Documentation**: This README and in-code comments describe design and usage.
- **Reporting**: Applicant’s choice (e.g. `reporting/dashboard.py` — Plotly).

## Prerequisites (Docker)

To run with `docker compose up` you need:

1. **Docker Desktop** installed: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. **Docker Desktop running** before you run any `docker` or `docker compose` command.

If you see:
```text
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```
then the Docker engine is not running. **Start Docker Desktop** (from the Windows Start menu), wait until it shows "Docker Desktop is running", then run `docker compose up` again.

## How to run

**After changing pipeline or ingestion code**, rebuild the pipeline image:  
`docker compose build pipeline` then `docker compose up`, or use `docker compose up --build`.

**Option A – Run everything (recommended)**  
The pipeline waits for the database and FastAPI to be ready, then runs ingestion + dbt and exits.

```bash
docker compose up
```

This starts `db`, `fastapi_app`, and `pipeline`. The pipeline container waits until both DB and API respond, then ingests data and runs `dbt run` to create the `curated_weather` view. When the pipeline finishes, its container exits; the DB and API keep running.

**Option B – Run the pipeline manually** (e.g. after starting only DB + API):

```bash
docker compose up -d db fastapi_app
# wait a few seconds, then:
docker compose run --rm pipeline
```

**Reporting** (optional, local Python):
   ```bash
   pip install -r requirements.txt
   export DB_URL=postgresql://postgres:Plan10boy%26@localhost:5432/MyDB
   python -m reporting.dashboard
   ```

## Local run (without Docker)

- Start Postgres and run the FastAPI app (e.g. `uvicorn` in `fastapi_app/`).
- From the project root:
  ```bash
  pip install -r requirements.txt
  python pipeline/orchestrator.py
  ```
- Optional: set `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `API_HOST`, `API_PORT` (or `API_URL`) to match your environment.

## Repository layout

| Path | Purpose |
|------|--------|
| `data/` | Public dataset (e.g. `DailyDelhiClimateTrain.csv`) |
| `fastapi_app/` | FastAPI app that serves fake weather data |
| `ingestion/` | Python scripts that load public CSV and FastAPI data into Postgres |
| `pipeline/` | Orchestrator: runs ingestion then `dbt run` |
| `dbt/` | dbt project: sources, staging models, curated view `curated_weather` |
| `reporting/` | Example reporting (Plotly dashboard) |
| `docker-compose.yml` | Defines `db`, `fastapi_app`, and `pipeline` services |

## Design choices

- **Single orchestration path**: The orchestrator runs Python ingestion then dbt so the curated dataset is always produced the same way.
- **dbt for transformation**: All cleaning and curation (rounding, union, `source` column) live in dbt models; no ad-hoc SQL in the repo.
- **Config via environment**: Database and API URLs are set by env vars so the same code works locally and in Docker.
