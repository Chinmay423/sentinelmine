.PHONY: help setup lint unit integration e2e security performance all clean coverage report

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = pytest
PYTEST_ARGS = -v
COVERAGE = coverage
UNIT_TEST_DIR = unit
INTEGRATION_TEST_DIR = integration
E2E_TEST_DIR = e2e
SECURITY_TEST_DIR = security
PERFORMANCE_TEST_DIR = performance
REPORT_DIR = reports

# Help target
help:
	@echo "SentinelMine Test Suite"
	@echo "======================="
	@echo "Available targets:"
	@echo "  setup        Install test dependencies"
	@echo "  lint         Run linting checks"
	@echo "  unit         Run unit tests"
	@echo "  integration  Run integration tests"
	@echo "  e2e          Run end-to-end tests"
	@echo "  security     Run security tests"
	@echo "  performance  Run performance tests"
	@echo "  all          Run all tests"
	@echo "  coverage     Run tests with coverage"
	@echo "  report       Generate HTML coverage report"
	@echo "  clean        Clean up temporary files"

# Setup target
setup:
	@echo "Installing test dependencies..."
	$(PIP) install -r requirements-test.txt

# Lint code
lint:
	@echo "Running lint checks..."
	flake8 ../src
	black --check ../src
	isort --check-only ../src
	mypy ../src

# Run unit tests
unit:
	@echo "Running unit tests..."
	$(PYTEST) $(PYTEST_ARGS) $(UNIT_TEST_DIR)

# Run integration tests
integration:
	@echo "Running integration tests..."
	$(PYTEST) $(PYTEST_ARGS) $(INTEGRATION_TEST_DIR) --run-integration

# Run end-to-end tests
e2e:
	@echo "Running end-to-end tests..."
	$(PYTEST) $(PYTEST_ARGS) $(E2E_TEST_DIR) --run-e2e

# Run security tests
security:
	@echo "Running security tests..."
	$(PYTEST) $(PYTEST_ARGS) $(SECURITY_TEST_DIR) --run-security

# Run performance tests
performance:
	@echo "Running performance tests..."
	$(PYTEST) $(PYTEST_ARGS) $(PERFORMANCE_TEST_DIR) --run-performance

# Run all tests
all: unit integration e2e security performance
	@echo "All tests completed."

# Run tests with coverage
coverage:
	@echo "Running tests with coverage..."
	$(COVERAGE) run -m pytest $(UNIT_TEST_DIR) $(INTEGRATION_TEST_DIR)
	$(COVERAGE) report -m

# Generate HTML coverage report
report: coverage
	@echo "Generating coverage report..."
	mkdir -p $(REPORT_DIR)
	$(COVERAGE) html -d $(REPORT_DIR)/coverage
	@echo "Report available at $(REPORT_DIR)/coverage/index.html"

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf $(UNIT_TEST_DIR)/__pycache__
	rm -rf $(INTEGRATION_TEST_DIR)/__pycache__
	rm -rf $(E2E_TEST_DIR)/__pycache__
	rm -rf $(SECURITY_TEST_DIR)/__pycache__
	rm -rf $(PERFORMANCE_TEST_DIR)/__pycache__
	rm -rf .coverage
	rm -rf $(REPORT_DIR)
	find . -name "*.pyc" -delete 