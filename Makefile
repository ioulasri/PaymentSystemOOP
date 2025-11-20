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
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"
	pip install pre-commit
	pre-commit install

# Testing
test:
	python test_runner.py

test-cov:
	python test_runner.py --coverage

test-fast:
	python test_runner.py --parallel

test-specific:
	@read -p "Enter test pattern: " pattern; \
	python test_runner.py --pattern "$$pattern"

# Code Quality
lint:
	flake8 src/ tests/
	bandit -r src/

format:
	black src/ tests/ test_runner.py
	isort src/ tests/ test_runner.py

type-check:
	mypy src/ test_runner.py

security:
	bandit -r src/
	safety check

# Pre-commit
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -f success.txt failed.txt test_results.json

# Building
build: clean
	python -m build

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Documentation index available at: file://$(PWD)/index.html"

serve-docs:
	@echo "Starting local documentation server..."
	python -m http.server 8000 --bind 127.0.0.1
	@echo "Documentation available at: http://localhost:8000"

# Running
run:
	python src/main.py

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
quick: format test-fast
	@echo "Quick development cycle complete!"