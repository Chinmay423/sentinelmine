# SentinelMine Testing Directory

This directory contains all test-related files and fixtures for the SentinelMine platform. Our testing approach follows security-first principles with comprehensive coverage across all system components.

## Directory Structure

```
tests/
├── unit/                # Unit tests for individual components
│   ├── frontend/        # React component tests
│   ├── api/             # API endpoint tests
│   ├── ml/              # ML model and algorithm tests
│   └── blockchain/      # Blockchain component tests
├── integration/         # Tests for component interactions
├── e2e/                 # End-to-end workflow tests
├── security/            # Security-focused tests
├── performance/         # Load and stress tests
└── fixtures/            # Test data and mock objects
```

## Running Tests

For detailed information on running tests, test coverage requirements, and CI integration, please refer to the comprehensive documentation in `docs/testing.md`.

## Test Development Guidelines

When adding new tests:

1. Follow the appropriate directory structure
2. Include detailed test descriptions
3. Create or update fixtures as needed
4. Ensure tests are deterministic and isolated
5. Add documentation for complex test scenarios

## Test Execution

Tests can be run using the test runner scripts in each directory. For more information on testing procedures and requirements, refer to `docs/TESTING.md`.

All components must maintain minimum test coverage as outlined in the testing documentation.

## Security Testing

Security testing adheres to NIST 800-53 and OWASP standards. Any security vulnerabilities discovered during testing should follow the responsible disclosure process outlined in the security policy document.

## Test Directory Structure

- **unit/**: Component-level unit tests
  - `frontend/`: Frontend component tests
  - `api/`: API service unit tests
  - `blockchain/`: Blockchain component tests
  - `ml/`: Machine learning model tests

- **integration/**: Tests for component interactions
  - `api_db/`: API to database integration
  - `frontend_api/`: Frontend to API integration
  - `blockchain_network/`: Blockchain network integration
  - `ml_services/`: ML model integration with services

- **security/**: Security-focused test suites
  - `sast/`: Static Application Security Testing configurations
  - `dast/`: Dynamic Application Security Testing scripts
  - `penetration/`: Penetration testing scenarios
  - `fuzzing/`: Fuzz testing configurations

- **performance/**: Performance and load testing
  - `api_load/`: API endpoint load tests
  - `db_stress/`: Database stress tests
  - `ml_inference/`: ML model inference latency tests
  - `blockchain_throughput/`: Blockchain transaction tests

## Running Tests

### Prerequisites

- Node.js 16+ for frontend tests
- Python 3.9+ for API and ML tests
- Rust toolchain for blockchain tests
- Docker and Docker Compose for integration tests

### Common Commands

```bash
# Run all unit tests
./scripts/run_unit_tests.sh

# Run integration tests
./scripts/run_integration_tests.sh

# Run security tests
./scripts/run_security_tests.sh

# Run performance benchmarks
./scripts/run_performance_tests.sh
```

## Continuous Integration

All tests are automatically executed in the CI/CD pipeline on every pull request and merge to main branches. See the `.github/workflows/` directory for CI configuration.

## Test Report Location

Test reports are generated in the `test-reports/` directory after test execution and are also available in the CI/CD pipeline dashboard.

## Contributing New Tests

When adding new functionality, please follow these guidelines:

1. Create corresponding unit tests for all new components
2. Update integration tests if component interfaces change
3. Add security tests for any security-sensitive features
4. Consider performance implications and add benchmarks if necessary 