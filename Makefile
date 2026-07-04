.PHONY: install format lint type-check test quality run validate-project validate-data assess-samples

PYTHON ?= python

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

format:
	ruff format .

lint:
	ruff check .

type-check:
	mypy .

test:
	pytest

quality: lint type-check test validate-project

run:
	$(PYTHON) -m app.main list-cases

validate-project:
	$(PYTHON) scripts/validate_project.py

validate-data:
	$(PYTHON) -m app.main validate-data

assess-samples:
	$(PYTHON) -m app.main assess-all
