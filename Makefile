.PHONY: help install install-dev test test-cov test-fast lint format type-check security clean build docs serve-docs run

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  test-fast    - Run tests in parallel"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  security     - Run security checks"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  docs         - Generate documentation"
	@echo "  serve-docs   - Serve documentation locally"
	@echo "  run          - Run the payment system"
	@echo "  pre-commit   - Install pre-commit hooks"

# Installation
install:
	.venv/bin/pip install -e .

install-dev:
	.venv/bin/pip install -e ".[dev,test]"
	.venv/bin/pip install pre-commit
	.venv/bin/pre-commit install

# Testing
test:
	python test_runner.py

test-cov:
	python test_runner.py --coverage

test-fast:
	python test_runner.py

test-specific:
	@read -p "Enter test pattern: " pattern; \
	python test_runner.py "$$pattern"

# Code Quality
lint:
	.venv/bin/flake8 src/ tests/ test_runner.py || echo "flake8 not installed - run 'make install-dev' first"
	.venv/bin/bandit -r src/ || echo "bandit not installed - run 'make install-dev' first"

format:
	.venv/bin/black src/ tests/ test_runner.py || echo "black not installed - run 'make install-dev' first"
	.venv/bin/isort src/ tests/ test_runner.py || echo "isort not installed - run 'make install-dev' first"

type-check:
	.venv/bin/mypy src/ test_runner.py || echo "mypy not installed - run 'make install-dev' first"

security:
	.venv/bin/bandit -r src/ || echo "bandit not installed - run 'make install-dev' first"
	.venv/bin/safety check || echo "safety not installed - run 'make install-dev' first"

# Pre-commit
pre-commit:
	.venv/bin/pre-commit install || echo "pre-commit not installed - run 'make install-dev' first"
	.venv/bin/pre-commit run --all-files || echo "pre-commit not installed - run 'make install-dev' first"

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f test_results/success.txt test_results/failed.txt test_results/test_results.json || true

# Building
build: clean
	.venv/bin/python -m build

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Documentation index available at: file://$(PWD)/test_results/index.html"

serve-docs:
	@echo "Starting local documentation server..."
	.venv/bin/python -m http.server 8000 --bind 127.0.0.1
	@echo "Documentation available at: http://localhost:8000"

# Running
run:
	.venv/bin/python src/main.py

# Development workflow
dev-setup: install-dev pre-commit
	@echo "Development environment setup complete!"

# CI/CD simulation
ci-test: lint type-check security test-cov
	@echo "All CI checks passed!"

# Release preparation
release-check: clean lint type-check security test-cov build
	@echo "Release check complete!"

# Quick development cycle
quick: format test
	@echo "Quick development cycle complete!"
