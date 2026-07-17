.PHONY: install lint type-check test coverage docs clean build

install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev,docs]"

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

test:
	pytest tests/ -v

coverage:
	pytest --cov=content_resource_api --cov-branch --cov-report=term-missing --cov-report=xml:build/coverage.xml --cov-report=html:build/coverage-html --cov-fail-under=95

docs:
	mkdocs build --strict

docs-serve:
	mkdocs serve

clean:
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ .ruff_cache/ __pycache__/ src/*.egg-info

security:
	bandit -r src/ -c bandit.yaml
