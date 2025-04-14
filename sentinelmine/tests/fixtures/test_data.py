"""
Test fixtures and mock data for use in various tests.
"""

import json
import os
import datetime
import pytest
import jwt
from unittest.mock import MagicMock

# Mock user data
MOCK_USERS = [
    {
        "id": "usr_123456",
        "username": "analyst1",
        "email": "analyst1@example.com",
        "role": "analyst",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2023-01-01T00:00:00Z",
        "last_login": "2023-05-15T10:30:00Z"
    },
    {
        "id": "usr_789012",
        "username": "admin1",
        "email": "admin1@example.com",
        "role": "admin",
        "first_name": "Jane",
        "last_name": "Smith",
        "created_at": "2023-01-01T00:00:00Z",
        "last_login": "2023-05-15T09:45:00Z"
    }
]

# Mock threat data for ML testing
MOCK_THREAT_DATA = [
    {
        "id": "threat_001",
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.5",
        "packet_size": 1024,
        "protocol": "TCP",
        "port": 80,
        "duration": 120,
        "frequency": 5,
        "bytes_transferred": 1024000,
        "time_of_day": 14.5,
        "day_of_week": 2,
        "threat_level": "low",
        "confidence": 0.85
    },
    {
        "id": "threat_002",
        "source_ip": "192.168.1.101",
        "destination_ip": "10.0.0.6",
        "packet_size": 2048,
        "protocol": "UDP",
        "port": 443,
        "duration": 60,
        "frequency": 10,
        "bytes_transferred": 2048000,
        "time_of_day": 2.5,
        "day_of_week": 5,
        "threat_level": "medium",
        "confidence": 0.75
    },
    {
        "id": "threat_003",
        "source_ip": "192.168.1.102",
        "destination_ip": "10.0.0.7",
        "packet_size": 4096,
        "protocol": "HTTP",
        "port": 8080,
        "duration": 30,
        "frequency": 20,
        "bytes_transferred": 4096000,
        "time_of_day": 18.3,
        "day_of_week": 1,
        "threat_level": "high",
        "confidence": 0.95
    }
]

# Mock dashboard metrics data
MOCK_DASHBOARD_METRICS = {
    "total_events": 12500,
    "events_by_severity": {
        "low": 8000,
        "medium": 3500,
        "high": 1000
    },
    "events_by_protocol": {
        "TCP": 6000,
        "UDP": 3000,
        "HTTP": 2500,
        "ICMP": 1000
    },
    "events_over_time": [
        {"timestamp": "2023-05-01T00:00:00Z", "count": 150},
        {"timestamp": "2023-05-02T00:00:00Z", "count": 175},
        {"timestamp": "2023-05-03T00:00:00Z", "count": 140},
        {"timestamp": "2023-05-04T00:00:00Z", "count": 160},
        {"timestamp": "2023-05-05T00:00:00Z", "count": 180}
    ],
    "top_source_ips": [
        {"ip": "192.168.1.100", "count": 450},
        {"ip": "192.168.1.101", "count": 320},
        {"ip": "192.168.1.102", "count": 280}
    ],
    "top_destination_ips": [
        {"ip": "10.0.0.5", "count": 400},
        {"ip": "10.0.0.6", "count": 350},
        {"ip": "10.0.0.7", "count": 300}
    ]
}

# Function to create a mock JWT token for testing
def create_mock_token(user_id="usr_123456", username="analyst1", role="analyst", 
                    expires_in=3600, secret="test-secret"):
    """Create a mock JWT token for testing purposes."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + datetime.timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

# Mock blockchain verification data
MOCK_BLOCKCHAIN_VERIFICATIONS = [
    {
        "id": "ver_123456",
        "data_hash": "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b",
        "block_number": 12345,
        "timestamp": "2023-05-15T10:30:00Z",
        "verified": True,
        "transaction_id": "0xabcdef1234567890abcdef1234567890"
    },
    {
        "id": "ver_789012",
        "data_hash": "0x0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
        "block_number": 12346,
        "timestamp": "2023-05-15T11:15:00Z",
        "verified": False,
        "transaction_id": "0x1234567890abcdef1234567890abcdef"
    }
]

# Pytest fixtures

@pytest.fixture
def mock_auth_token():
    """Return a mock authentication token."""
    return create_mock_token()

@pytest.fixture
def mock_admin_token():
    """Return a mock authentication token with admin privileges."""
    return create_mock_token(user_id="usr_789012", username="admin1", role="admin")

@pytest.fixture
def mock_user_data():
    """Return mock user data."""
    return MOCK_USERS

@pytest.fixture
def mock_threat_data():
    """Return mock threat data."""
    return MOCK_THREAT_DATA

@pytest.fixture
def mock_dashboard_data():
    """Return mock dashboard metrics data."""
    return MOCK_DASHBOARD_METRICS

@pytest.fixture
def mock_blockchain_data():
    """Return mock blockchain verification data."""
    return MOCK_BLOCKCHAIN_VERIFICATIONS

@pytest.fixture
def mock_ml_model():
    """Create a mock ML model for testing."""
    model = MagicMock()
    # Set up predictions for different inputs
    model.predict.side_effect = lambda x: ["low", "medium", "high"][len(x) % 3]
    model.predict_proba.return_value = [[0.7, 0.2, 0.1], [0.1, 0.7, 0.2], [0.1, 0.2, 0.7]]
    return model 