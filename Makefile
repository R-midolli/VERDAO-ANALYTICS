.PHONY: help setup data run test lint

help:
	@echo ""
	@echo "🌿 Verdão Analytics"
	@echo "==================="
	@echo "make setup        → uv venv + install deps"
	@echo "make data         → extract FBref & TheSportsDB data"
	@echo "make run          → Streamlit dashboard"
	@echo "make test         → pytest + coverage"
	@echo "make lint         → ruff + black"
	@echo ""

setup:
	pip install uv
	uv venv
	uv pip install -r requirements-full.txt
	@echo "✅ Setup done. Run: source .venv/Scripts/activate"

data:
	uv run python src/data_loader.py

run:
	uv run streamlit run app.py

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/ app.py pages/
	uv run black --check src/ tests/ app.py pages/
