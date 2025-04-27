# Makefile for portmgr

# Run unit tests with coverage
test:
	pytest --cov=core --cov-report=term --cov-report=html

coverage:
	pytest --cov=core --cov-report=term --cov-report=html
	open htmlcov/index.html || xdg-open htmlcov/index.html || echo "Coverage report generated in htmlcov/index.html"

# Clean Python bytecode and coverage
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +
	rm -rf .pytest_cache .coverage htmlcov

# Install dev dependencies
install-dev:
	pip install -e .[dev]

# Show test coverage report in browser
coverage:
	open htmlcov/index.html

# Format code with black
format:
	black core/ tests/

# Lint with flake8
lint:
	flake8 core/ --max-line-length=100

.PHONY: test clean install-dev coverage format lint
