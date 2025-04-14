# SentinelMine Testing Guide

This document outlines the testing strategy, procedures, and frameworks used for ensuring the quality and security of the SentinelMine platform.

## Table of Contents
- [Testing Philosophy](#testing-philosophy)
- [Testing Environments](#testing-environments)
- [Test Categories](#test-categories)
- [Frontend Testing](#frontend-testing)
- [API Testing](#api-testing)
- [ML Component Testing](#ml-component-testing)
- [Blockchain Testing](#blockchain-testing)
- [Integration Testing](#integration-testing)
- [Security Testing](#security-testing)
- [Performance Testing](#performance-testing)
- [Continuous Integration](#continuous-integration)
- [Test Data Management](#test-data-management)

## Testing Philosophy

SentinelMine follows a comprehensive testing philosophy:

1. **Security-First Testing**: Security validation is an integral part of all testing phases, not a separate concern
2. **Shift-Left Approach**: Testing begins early in the development lifecycle
3. **Automation Priority**: Automated tests are preferred over manual verification
4. **Continuous Testing**: Tests run automatically with each code change
5. **Realistic Test Data**: Tests use realistic (but anonymized) data that reflects production usage

## Testing Environments

### Development Environment
- Runs on developer machines or CI pipelines
- Uses mocked external dependencies
- Focuses on unit and component tests
- Configuration in `config/dev`

### Integration Environment
- Shared environment for integration testing
- Uses containerized services
- Tests inter-component communication
- Configuration in `config/integration`

### Staging Environment
- Production-like environment
- Complete infrastructure deployment
- Used for performance and security testing
- Configuration in `config/staging`

### Classified Testing Environment
- Air-gapped environment for testing with classified data
- Physical security controls
- Limited access to security-cleared personnel
- Configuration in `config/classified`

## Test Categories

### Unit Tests
- Test individual functions and methods
- High code coverage (target: >85%)
- Fast execution (<1s per test)
- Run on every commit

### Component Tests
- Test individual components in isolation
- Use mocked dependencies
- Validate component interfaces
- Run on every commit

### Integration Tests
- Verify interactions between components
- Test API contracts
- Validate data flows
- Run on feature branches and main branch

### End-to-End Tests
- Test complete user journeys
- Validate system behavior from user perspective
- Run in staging environment
- Run before releases

### Security Tests
- SAST (Static Application Security Testing)
- DAST (Dynamic Application Security Testing)
- Dependency scanning
- Container scanning
- Run on feature branches and main branch

### Performance Tests
- Load testing
- Stress testing
- Endurance testing
- Run in staging environment before releases

## Frontend Testing

### Unit Testing
```bash
# Run unit tests
cd src/frontend
npm test

# Run with coverage report
npm test -- --coverage
```

### Component Testing
Frontend component tests use React Testing Library and Jest:

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '../components/auth/LoginForm';

test('LoginForm submits with username and password', () => {
  // Arrange
  const handleSubmit = jest.fn();
  render(<LoginForm onSubmit={handleSubmit} />);
  
  // Act
  fireEvent.change(screen.getByLabelText(/username/i), {
    target: { value: 'testuser' },
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password123' },
  });
  fireEvent.click(screen.getByRole('button', { name: /login/i }));
  
  // Assert
  expect(handleSubmit).toHaveBeenCalledWith({
    username: 'testuser',
    password: 'password123',
  });
});
```

### End-to-End Testing
E2E tests use Cypress:

```javascript
describe('Authentication', () => {
  it('should login with valid credentials', () => {
    cy.visit('/login');
    cy.get('[data-testid=username-input]').type('analyst');
    cy.get('[data-testid=password-input]').type('secure_password');
    cy.get('[data-testid=login-button]').click();
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid=user-profile]').should('be.visible');
  });
});
```

## API Testing

### Unit Testing
API unit tests use pytest:

```python
def test_verify_password():
    """Test password verification function."""
    # Given
    plain_password = "secure_password"
    hashed_password = get_password_hash(plain_password)
    
    # When
    result = verify_password(plain_password, hashed_password)
    
    # Then
    assert result is True
```

### Integration Testing
API integration tests:

```python
@pytest.mark.asyncio
async def test_login_endpoint():
    """Test login endpoint with valid credentials."""
    # Given
    app = get_test_app()
    client = AsyncClient(app=app, base_url="http://test")
    login_data = {
        "username": "test_user",
        "password": "secure_password"
    }
    
    # When
    response = await client.post("/api/auth/login", json=login_data)
    
    # Then
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
```

### API Contract Testing
API contract tests using Pact:

```python
def test_prediction_service_contract():
    """Test the contract between API and ML service."""
    # Define the contract
    pact = Pact(consumer="api", provider="ml-service")
    
    # Define the expected interaction
    pact.given("ML model is ready")
        .upon_receiving("a prediction request")
        .with_request("POST", "/predict", body={"data": {...}})
        .will_respond_with(200, body={"prediction": {...}})
    
    # Verify the contract
    with pact:
        result = prediction_service.predict({"data": {...}})
        assert "prediction" in result
```

## ML Component Testing

### Model Unit Testing
```python
def test_threat_assessment_model():
    """Test threat assessment model predictions."""
    # Given
    model = load_model("threat_assessment")
    test_input = {...}  # Test input data
    
    # When
    prediction = model.predict(test_input)
    
    # Then
    assert isinstance(prediction, dict)
    assert "threat_level" in prediction
    assert 0 <= prediction["threat_level"] <= 1
```

### Model Validation Testing
```python
def test_model_accuracy():
    """Test model meets accuracy requirements."""
    # Given
    model = load_model("threat_assessment")
    test_dataset = load_test_dataset()
    
    # When
    metrics = evaluate_model(model, test_dataset)
    
    # Then
    assert metrics["accuracy"] >= 0.9
    assert metrics["f1_score"] >= 0.85
    assert metrics["false_positive_rate"] <= 0.05
```

### Model Robustness Testing
```python
def test_model_robustness():
    """Test model robustness against adversarial inputs."""
    # Given
    model = load_model("threat_assessment")
    test_input = {...}  # Normal input
    adversarial_input = generate_adversarial_input(test_input)
    
    # When
    normal_prediction = model.predict(test_input)
    adversarial_prediction = model.predict(adversarial_input)
    
    # Then
    assert normal_prediction["threat_level"] > 0.7
    assert abs(normal_prediction["threat_level"] - adversarial_prediction["threat_level"]) < 0.1
```

## Blockchain Testing

### Chaincode Unit Testing
```go
func TestCreateRecord(t *testing.T) {
    // Given
    ctx := createMockContext()
    contract := new(SecurityOpsContract)
    
    // When
    err := contract.CreateRecord(ctx, "record-001", "threat", "user-001", 
                              "{\"level\":\"high\"}", "hash123", "secret", "intel")
    
    // Then
    assert.NoError(t, err)
    
    // Verify record was created
    recordJSON, err := ctx.GetStub().GetState("record-001")
    assert.NoError(t, err)
    assert.NotNil(t, recordJSON)
    
    var record SecurityRecord
    err = json.Unmarshal(recordJSON, &record)
    assert.NoError(t, err)
    assert.Equal(t, "threat", record.Type)
}
```

### Blockchain Integration Testing
```go
func TestVerificationFlow(t *testing.T) {
    // Given
    network := SetupTestNetwork()
    client := network.GetClient("org1")
    
    // Create a record
    recordID := "test-" + uuid.New().String()
    createResp, err := client.CreateRecord(recordID, "test", "data")
    assert.NoError(t, err)
    assert.Equal(t, "success", createResp.Status)
    
    // When - Verify the record
    verifyResp, err := client.VerifyRecord(recordID)
    
    // Then
    assert.NoError(t, err)
    assert.Equal(t, "verified", verifyResp.Status)
    
    // Check audit trail
    record, err := client.GetRecord(recordID)
    assert.NoError(t, err)
    assert.NotNil(t, record.Verification)
    assert.NotEmpty(t, record.Verification.BlockNumber)
}
```

## Integration Testing

### System Integration Test
```python
def test_prediction_end_to_end():
    """Test complete prediction flow from API to blockchain verification."""
    # Given
    client = TestClient(app)
    auth_response = client.post("/api/auth/login", json={
        "username": "analyst",
        "password": "test_password"
    })
    token = auth_response.json()["access_token"]
    
    # When - Create prediction
    prediction_data = {
        "prediction_type": "threat_assessment",
        "input_data": {...}
    }
    prediction_response = client.post(
        "/api/predictions",
        json=prediction_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    prediction_id = prediction_response.json()["id"]
    
    # Verify prediction was created
    get_response = client.get(
        f"/api/predictions/{prediction_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Then verify blockchain record was created
    verify_response = client.post(
        f"/api/predictions/{prediction_id}/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Assert
    assert prediction_response.status_code == 201
    assert get_response.status_code == 200
    assert verify_response.status_code == 200
    assert verify_response.json()["verified"] == True
```

## Security Testing

### SAST (Static Analysis)
```bash
# Run static analysis
./ops/scripts/run-sast.sh

# Example output
# Analyzing src/api/...
# Analyzing src/frontend/...
# Analyzing src/ml/...
# Found 0 critical issues, 2 medium issues, 5 info issues
```

### DAST (Dynamic Analysis)
```bash
# Run ZAP against the API
./ops/scripts/run-zap.sh --target https://staging-api.sentinelmine.org

# Run OWASP validation
./ops/scripts/run-owasp-validation.sh
```

### Security Scanning
```bash
# Scan dependencies
./ops/scripts/scan-dependencies.sh

# Scan Docker images
./ops/scripts/scan-containers.sh

# Run comprehensive security scan
./ops/scripts/security-scan.sh --scope full
```

## Performance Testing

### Load Testing
```bash
# Run load test with 1000 virtual users
./ops/scripts/load-test.sh --users 1000 --duration 5m

# Expected results:
# API response time p95: < 500ms
# Database CPU utilization: < 70%
# Error rate: < 0.1%
```

### Stress Testing
```bash
# Run stress test with gradually increasing load
./ops/scripts/stress-test.sh --start-users 100 --end-users 5000 --step 500

# Expected results:
# Max throughput: > 1000 RPS
# Breaking point: > 3000 concurrent users
```

## Continuous Integration

SentinelMine uses a multi-stage CI pipeline:

1. **Build Stage**
   - Compile code
   - Run linters
   - Run unit tests
   - Generate artifacts

2. **Test Stage**
   - Run component tests
   - Run integration tests
   - Generate test reports

3. **Security Stage**
   - Run SAST scans
   - Run dependency scanning
   - Run container scanning
   - Generate security reports

4. **Deployment Stage**
   - Deploy to staging
   - Run smoke tests
   - Run performance tests
   - Generate performance reports

## Test Data Management

### Test Data Generation
```bash
# Generate synthetic test data
./ops/scripts/generate-test-data.sh --records 1000 --output ./test-data

# Import test data
./ops/scripts/import-test-data.sh --source ./test-data --target dev
```

### Data Anonymization
```bash
# Anonymize production data for testing
./ops/scripts/anonymize-data.sh --source prod-backup --output test-data

# Available anonymization techniques:
# - Value masking
# - Shuffling
# - Synthetic generation
# - Encryption
```

### Classified Test Data
For testing with classified data, follow the secure data handling procedures:

1. Access the air-gapped testing environment
2. Use the physical access token to authenticate
3. Run tests using the classified data workflow:
   ```bash
   ./ops/classified/run-tests.sh --dataset classified-001
   ```
4. Review test results within the classified environment
5. Export sanitized test reports through the data diode 