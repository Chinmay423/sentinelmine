"""
Global pytest configuration for the SentinelMine test suite.
This file is automatically discovered by pytest when tests are run.
"""

import pytest
import os
import sys
import logging
from dotenv import load_dotenv

# Import fixtures from fixture modules
from tests.fixtures.test_data import (
    mock_auth_token, 
    mock_admin_token, 
    mock_user_data, 
    mock_threat_data, 
    mock_dashboard_data, 
    mock_blockchain_data,
    mock_ml_model
)

# Setup logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env.test if it exists
if os.path.exists(".env.test"):
    load_dotenv(".env.test")
else:
    load_dotenv()  # Fall back to regular .env

# Add the src directory to the Python path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--run-integration", action="store_true", default=False, help="run integration tests"
    )
    parser.addoption(
        "--run-e2e", action="store_true", default=False, help="run end-to-end tests"
    )
    parser.addoption(
        "--run-security", action="store_true", default=False, help="run security tests"
    )
    parser.addoption(
        "--run-performance", action="store_true", default=False, help="run performance tests"
    )

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "security: mark test as security test")
    config.addinivalue_line("markers", "performance: mark test as performance test")

def pytest_collection_modifyitems(config, items):
    """
    Skip tests based on command line options.
    By default, only run unit tests.
    """
    # Define markers for different test types
    skip_slow = pytest.mark.skip(reason="use --run-slow option to run")
    skip_integration = pytest.mark.skip(reason="use --run-integration option to run")
    skip_e2e = pytest.mark.skip(reason="use --run-e2e option to run")
    skip_security = pytest.mark.skip(reason="use --run-security option to run")
    skip_performance = pytest.mark.skip(reason="use --run-performance option to run")
    
    # Check for command line options
    run_slow = config.getoption("--run-slow")
    run_integration = config.getoption("--run-integration")
    run_e2e = config.getoption("--run-e2e")
    run_security = config.getoption("--run-security")
    run_performance = config.getoption("--run-performance")
    
    # Skip tests based on options
    for item in items:
        if "slow" in item.keywords and not run_slow:
            item.add_marker(skip_slow)
        if "integration" in item.keywords and not run_integration:
            item.add_marker(skip_integration)
        if "e2e" in item.keywords and not run_e2e:
            item.add_marker(skip_e2e)
        if "security" in item.keywords and not run_security:
            item.add_marker(skip_security)
        if "performance" in item.keywords and not run_performance:
            item.add_marker(skip_performance)

@pytest.fixture(scope="session")
def test_env():
    """Return test environment information."""
    return {
        "env": os.environ.get("TEST_ENV", "development"),
        "api_url": os.environ.get("TEST_API_URL", "http://localhost:5000"),
        "frontend_url": os.environ.get("TEST_FRONTEND_URL", "http://localhost:3000"),
        "ml_url": os.environ.get("TEST_ML_URL", "http://localhost:5001"),
        "blockchain_url": os.environ.get("TEST_BLOCKCHAIN_URL", "http://localhost:5002")
    }

@pytest.fixture(scope="session", autouse=True)
def setup_teardown():
    """Setup and teardown for the entire test session."""
    # Setup
    logging.info("Setting up test environment")
    
    # Yield control back to the tests
    yield
    
    # Teardown
    logging.info("Tearing down test environment") 