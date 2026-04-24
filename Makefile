.PHONY: lint test

lint:
	ruff check . && ruff format --check .
	mypy app
	bandit -r app -ll
	PIPAPI_PYTHON_LOCATION=$(shell which python) pip-audit --ignore-vuln CVE-2026-1703 --ignore-vuln CVE-2026-3219

test:
	pytest -v --cov=app --cov-report=term-missing --cov-fail-under=90
