.PHONY: help install install-dev test lint format clean analyze

help:
	@echo "Available targets:"
	@echo "  install     - Install package in production mode"
	@echo "  install-dev - Install with development dependencies"
	@echo "  test        - Run pytest with coverage"
	@echo "  lint        - Run linters (black, isort, flake8)"
	@echo "  format      - Auto-format code"
	@echo "  clean       - Remove build artifacts"
	@echo "  analyze     - Run self-analysis"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	PYTHONPATH=src pytest tests/ -v --cov=src/core --cov-report=term-missing

lint:
	black --check src/ tests/
	isort --check src/ tests/

format:
	black src/ tests/
	isort src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

analyze:
	./collider full . --output .collider
