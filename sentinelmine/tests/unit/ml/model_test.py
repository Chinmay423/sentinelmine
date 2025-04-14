import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import joblib
import os

# Import the model predictor (adjust path as needed)
from src.ml.predictor import predict_threat_level, load_model

@pytest.fixture
def mock_model():
    """Create a mock ML model for testing."""
    model = MagicMock()
    # Configure the mock model to return specific predictions
    model.predict.return_value = np.array([0.2, 0.7, 0.1])
    model.predict_proba.return_value = np.array([[0.2, 0.7, 0.1]])
    return model

@patch('src.ml.predictor.load_model')
def test_predict_threat_level(mock_load_model, mock_model):
    """Test threat level prediction functionality."""
    # Configure the mock to return our mock model
    mock_load_model.return_value = mock_model
    
    # Test input data
    test_data = {
        "source_ip": "192.168.1.1",
        "destination_ip": "10.0.0.1",
        "packet_size": 1024,
        "protocol": "TCP",
        "port": 443,
        "duration": 120,
        "frequency": 5,
        "bytes_transferred": 1024000,
        "time_of_day": 14.5,
        "day_of_week": 2
    }
    
    # Call the prediction function
    result = predict_threat_level(test_data)
    
    # Verify the result structure
    assert isinstance(result, dict)
    assert "threat_level" in result
    assert "confidence" in result
    assert "raw_scores" in result
    
    # Check that the highest probability class was selected
    assert result["threat_level"] == "medium"  # Based on mock model returning [0.2, 0.7, 0.1]
    assert result["confidence"] == 0.7
    assert result["raw_scores"] == {"low": 0.2, "medium": 0.7, "high": 0.1}
    
    # Verify the model was loaded correctly
    mock_load_model.assert_called_once()

def test_load_model():
    """Test the model loading functionality."""
    # Mock joblib.load to return our mock model
    with patch('joblib.load') as mock_joblib:
        mock_model = MagicMock()
        mock_joblib.return_value = mock_model
        
        # Set up environment for model path (assuming model path is from env var)
        with patch.dict(os.environ, {"MODEL_PATH": "/path/to/model.pkl"}):
            model = load_model()
            
            # Verify the model was loaded from the correct path
            mock_joblib.assert_called_once_with("/path/to/model.pkl")
            
            # Verify the returned model is our mock
            assert model == mock_model

def test_model_preprocessing():
    """Test the preprocessing of input data for the model."""
    # Test with missing fields
    with pytest.raises(ValueError, match="Missing required fields"):
        incomplete_data = {"source_ip": "192.168.1.1"}  # Missing most fields
        predict_threat_level(incomplete_data)
    
    # Test with invalid data types
    with pytest.raises(ValueError, match="Invalid data type"):
        invalid_data = {
            "source_ip": "192.168.1.1",
            "destination_ip": "10.0.0.1",
            "packet_size": "not a number",  # Should be integer
            "protocol": "TCP",
            "port": 443,
            "duration": 120,
            "frequency": 5,
            "bytes_transferred": 1024000,
            "time_of_day": 14.5,
            "day_of_week": 2
        }
        predict_threat_level(invalid_data) 