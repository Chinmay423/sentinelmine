import pytest
import json
from unittest.mock import patch, MagicMock
from src.api.app import app

@pytest.fixture
def client():
    """Create a test client for the API."""
    with app.test_client() as client:
        yield client

def test_login_route_valid_credentials(client):
    """Test login route with valid credentials."""
    # Mock the authentication function
    with patch('src.api.routes.auth.authenticate_user') as mock_auth:
        # Setup the mock to return successful authentication
        mock_auth.return_value = {
            'user_id': '12345',
            'username': 'testuser',
            'role': 'analyst',
            'token': 'fake-jwt-token'
        }
        
        # Send POST request to login endpoint
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert data['token'] == 'fake-jwt-token'
        assert data['user']['username'] == 'testuser'
        assert data['user']['role'] == 'analyst'
        
        # Verify authenticate_user was called with correct params
        mock_auth.assert_called_once_with('testuser', 'password123')

def test_login_route_invalid_credentials(client):
    """Test login route with invalid credentials."""
    # Mock the authentication function
    with patch('src.api.routes.auth.authenticate_user') as mock_auth:
        # Setup the mock to simulate authentication failure
        mock_auth.return_value = None
        
        # Send POST request to login endpoint
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        # Check response
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid credentials'

def test_validate_token_valid(client):
    """Test token validation with a valid token."""
    # Mock the token validation function
    with patch('src.api.routes.auth.validate_token') as mock_validate:
        # Setup the mock to return user data
        mock_validate.return_value = {
            'user_id': '12345',
            'username': 'testuser',
            'role': 'analyst'
        }
        
        # Send GET request to validate token endpoint
        response = client.get(
            '/api/auth/validate',
            headers={'Authorization': 'Bearer fake-jwt-token'}
        )
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] is True
        assert data['user']['username'] == 'testuser'
        
        # Verify validate_token was called with correct token
        mock_validate.assert_called_once_with('fake-jwt-token')

def test_validate_token_invalid(client):
    """Test token validation with an invalid token."""
    # Mock the token validation function
    with patch('src.api.routes.auth.validate_token') as mock_validate:
        # Setup the mock to raise an exception
        mock_validate.side_effect = Exception('Invalid token')
        
        # Send GET request to validate token endpoint
        response = client.get(
            '/api/auth/validate',
            headers={'Authorization': 'Bearer invalid-token'}
        )
        
        # Check response
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['valid'] is False
        assert 'error' in data 