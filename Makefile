# Data Engineer Project - Makefile
# Prerequisites: Docker Desktop, Make (Git for Windows includes make; or WSL)
# From fresh clone: make setup && make run

.PHONY: setup run test report clean help

# Default Unix; override for Windows
PYTHON := .venv/bin/python
PIP := .venv/bin/pip
ifeq ($(OS),Windows_NT)
  PYTHON := .venv/Scripts/python.exe
  PIP := .venv/Scripts/pip.exe
endif

help:
	@echo "Targets: setup, run, test, report, clean"

setup:
	python -m venv .venv
	$(PIP) install -r requirements.txt
	docker compose build

run:
	docker compose up --build

test:
	$(PYTHON) -m pytest tests/ -v

report:
	$(PYTHON) -m reporting.dashboard

clean:
	docker compose down -v 2>/dev/null || true
	rm -rf venv .venv
	rm -rf __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
