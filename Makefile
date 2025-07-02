# Makefile for realloc

# Run unit tests with coverage
test:
	pytest --cov=realloc --cov-report=term --cov-report=html

coverage:
	pytest --cov=realloc --cov-report=term --cov-report=html
	open htmlcov/index.html || xdg-open htmlcov/index.html || echo "Coverage report generated in htmlcov/index.html"

# Clean Python bytecode and coverage
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +
	rm -rf .pytest_cache .coverage htmlcov

# Install dev dependencies
install-dev:
	pip install -e .[dev]

# Format code with black
format:
	black src/ tests/

# Lint with flake8
lint:
	flake8 src/ --max-line-length=100

# Build package distributions
build-clean:
	rm -rf build/ dist/ src/*.egg-info/

build:
	python -m build

# Build and clean in one command
build-all: build-clean build

# Install latest build
install-build:
	pip install dist/*.whl



.PHONY: test clean install-dev coverage format lint build build-clean build-all install-build
