.PHONY: install format lint type-check test quality run validate-project

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
	$(PYTHON) -m app.main

validate-project:
	$(PYTHON) scripts/validate_project.py
