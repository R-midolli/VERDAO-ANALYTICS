.PHONY: help setup data transform train run orchestrate test lint

help:
	@echo ""
	@echo "🌿 Verdão AI Empire"
	@echo "==================="
	@echo "make setup        → uv venv + install deps"
	@echo "make data         → extract all data sources"
	@echo "make transform    → feature engineering"
	@echo "make train        → train all ML models"
	@echo "make run          → Streamlit dashboard"
	@echo "make orchestrate  → start Prefect server + deploy flows"
	@echo "make test         → pytest + coverage"
	@echo "make lint         → ruff + black"
	@echo ""

setup:
	pip install uv
	uv venv
	uv pip install -r requirements-full.txt
	@echo "✅ Setup done. Run: source .venv/Scripts/activate"

data:
	uv run python -m orchestration.flows.daily_elt

transform:
	uv run python -m src.transform.players
	uv run python -m src.transform.matches

train:
	uv run python -m src.ml.performance
	uv run python -m src.ml.injury
	uv run python -m src.ml.match_outcome
	uv run python -m src.ml.clustering

run:
	uv run streamlit run src/dashboard/app.py

orchestrate:
	uv run prefect server start &
	sleep 3
	uv run python orchestration/prefect_config.py

test:
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	uv run ruff check src/ orchestration/ tests/
	uv run black --check src/ orchestration/ tests/
