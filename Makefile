.PHONY: setup demo test coverage lint format api analyze validate clean

PYTHON ?= python

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

demo:
	$(PYTHON) scripts/generate_demo_data.py

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

coverage:
	$(PYTHON) -m pytest --cov=finops --cov-report=term-missing --cov-report=xml

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format:
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

api:
	FINOPS_DATA_DIR=data/demo uvicorn finops.api:app --app-dir src --host 0.0.0.0 --port 8080

analyze:
	PYTHONPATH=src $(PYTHON) -m finops.cli --data-dir data/demo analyze --output reports/demo-analysis.json

validate:
	PYTHONPATH=src $(PYTHON) scripts/verify_repository.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -r {} +
	rm -rf .pytest_cache .ruff_cache htmlcov coverage.xml .coverage
