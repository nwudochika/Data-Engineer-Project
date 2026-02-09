# Data Engineer Project

Data pipeline: ingest public + FastAPI fake weather data → PostgreSQL → dbt (curated view) → reporting.

## Quick Start (from fresh clone)

**Prerequisites:** Docker Desktop (running), Make, Python 3.10+

```bash
make setup
make run
```

Then (optional): `make test`, `make report`.

- **make setup**: creates `.venv`, installs Python deps, builds Docker images.
- **make run**: starts DB + FastAPI + pipeline (pipeline runs once and exits).
- **make test**: runs pytest in `tests/`.
- **make report**: runs the Plotly dashboard (requires pipeline to have run and DB up).
- **make clean**: removes containers, volumes, venv, caches.

## Deliverables Checklist

| Item | Location |
|------|----------|
| Makefile (setup, run, test, report, clean) | `Makefile` |
| docker-compose.yml | `docker-compose.yml` |
| .env.example | `.env.example` |
| docs/architecture.md | `docs/architecture.md` |
| docs/decisions.md | `docs/decisions.md` |
| docs/er_diagram.png | `docs/er_diagram.png` |
| README with setup instructions | This file |
| Tests | `tests/` |
| .env in .gitignore | `.gitignore` |

## Components

- **API**: FastAPI app in `fastapi_app/` — serves fake weather at `/fake_weather?days=N`.
- **Ingestion**: `ingestion/` — Python scripts load CSV and API data into Postgres.
- **Orchestration**: `pipeline/orchestrator.py` — waits for DB/API, drops prior dbt views, runs ingestion, runs `dbt run`.
- **Database**: PostgreSQL 15 via Docker.
- **dbt**: `dbt/` — staging and curated view `curated_weather` (schema `public_public`).
- **Reports**: `reporting/dashboard.py` — Plotly line chart from `curated_weather`.

## Configuration

Copy `.env.example` to `.env` and set variables (e.g. `DB_PASSWORD`). Do not commit `.env`.  
For Docker, defaults in `docker-compose.yml` work without a `.env` file.

## Repository Layout

| Path | Purpose |
|------|--------|
| `data/` | Public dataset CSV |
| `fastapi_app/` | Fake weather API |
| `ingestion/` | Python ingestion scripts |
| `pipeline/` | Orchestrator |
| `dbt/` | dbt project (sources, staging, curated) |
| `reporting/` | Dashboard script |
| `tests/` | Pytest tests |
| `docs/` | Architecture, decisions, ER diagram |

## Prerequisites (Docker)

Docker Desktop must be **installed and running**. If you see `The system cannot find the file specified` for `dockerDesktopLinuxEngine`, start Docker Desktop and try again.

## After Code Changes

Rebuild the pipeline image so the container uses your changes:

```bash
docker compose up --build
```

Or: `docker compose build pipeline` then `docker compose up`.
