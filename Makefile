.PHONY: install format lint type-check test quality run validate-project validate-data assess-samples validate-mcp list-mcp test-mcp validate-skills list-skills test-skills mock-mcp-demo

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

validate-mcp:
	$(PYTHON) -m app.main validate-mcp-config

list-mcp:
	$(PYTHON) -m app.main list-mcp-servers

test-mcp:
	pytest tests/unit/test_mcp_interop.py tests/integration/test_cli.py

validate-skills:
	$(PYTHON) -m app.main list-skills

list-skills:
	$(PYTHON) -m app.main list-skills

test-skills:
	pytest tests/unit/test_skills.py tests/integration/test_cli.py

mock-mcp-demo:
	$(PYTHON) -m app.main agent-assess --case-id SYN-CANCER-2WW-001 --mode mock-mcp --json
