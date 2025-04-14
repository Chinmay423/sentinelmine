import os
import json
import logging
import time
from datetime import datetime
import uuid
from typing import Dict, Any, List, Optional, Union

from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import torch
import tensorflow as tf
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ml_service.log")
    ]
)
logger = logging.getLogger(__name__)

# Check if GPU is available
if torch.cuda.is_available():
    logger.info(f"GPU is available: {torch.cuda.get_device_name(0)}")
    device = "cuda"
else:
    logger.info("GPU not available, using CPU")
    device = "cpu"

# Model registry - would be replaced with real models in production
MODEL_REGISTRY = {
    "threat_assessment": {
        "name": "threat-assessment-model-v1",
        "type": "transformer",
        "version": "1.0.0",
        "loaded": False,
        "instance": None
    },
    "network_intrusion": {
        "name": "network-intrusion-detection-v2",
        "type": "pytorch",
        "version": "2.1.0",
        "loaded": False,
        "instance": None
    },
    "social_media_analysis": {
        "name": "social-media-sentiment-v1",
        "type": "transformer",
        "version": "1.2.0",
        "loaded": False,
        "instance": None
    },
    "geopolitical_risk": {
        "name": "geopolitical-risk-assessment-v1",
        "type": "ensemble",
        "version": "1.0.0",
        "loaded": False,
        "instance": None
    },
    "disinformation_detection": {
        "name": "disinformation-classifier-v3",
        "type": "transformer",
        "version": "3.0.1",
        "loaded": False,
        "instance": None
    }
}

# Lazy load models as needed
def load_model(model_type: str) -> bool:
    """
    Load a model on demand. This simulates loading different models.
    In production, this would load actual ML models.
    """
    if model_type not in MODEL_REGISTRY:
        logger.error(f"Unknown model type: {model_type}")
        return False
        
    model_info = MODEL_REGISTRY[model_type]
    
    if model_info["loaded"]:
        logger.info(f"Model {model_type} already loaded")
        return True
        
    try:
        logger.info(f"Loading model {model_type} ({model_info['name']} v{model_info['version']})")
        
        # Simulate model loading time
        time.sleep(2)
        
        # In production, we would load actual models here
        # For demonstration, we'll just create placeholder objects
        if model_info["type"] == "transformer":
            # Load a simple sentiment analysis model as placeholder
            try:
                model = pipeline("sentiment-analysis", device=0 if device == "cuda" else -1)
                model_info["instance"] = model
            except Exception as e:
                logger.warning(f"Could not load transformer model with GPU: {str(e)}")
                model = pipeline("sentiment-analysis", device=-1)
                model_info["instance"] = model
                
        elif model_info["type"] == "pytorch":
            # Create a simple PyTorch model as placeholder
            class SimpleModel(torch.nn.Module):
                def __init__(self):
                    super().__init__()
                    self.fc = torch.nn.Linear(10, 2)
                    
                def forward(self, x):
                    return torch.nn.functional.softmax(self.fc(x), dim=1)
                    
            model = SimpleModel()
            if device == "cuda":
                model = model.cuda()
            model_info["instance"] = model
            
        elif model_info["type"] == "ensemble":
            # Simulate an ensemble model
            model_info["instance"] = {
                "models": ["Model1", "Model2", "Model3"],
                "weights": [0.5, 0.3, 0.2]
            }
            
        model_info["loaded"] = True
        logger.info(f"Successfully loaded model {model_type}")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model {model_type}: {str(e)}")
        return False

# Prediction functions for different model types
def predict_threat_assessment(data: Dict[str, Any]) -> Dict[str, Any]:
    """Simulated prediction for threat assessment"""
    model_type = "threat_assessment"
    
    if not MODEL_REGISTRY[model_type]["loaded"]:
        load_model(model_type)
        
    # Extract features from input data
    indicators = data.get("indicators", [])
    sources = data.get("sources", [])
    timeframe = data.get("timeframe", "immediate")
    
    # In production, we'd process this with the actual model
    # For demo, generate simulated results
    threat_levels = ["low", "medium", "high", "critical"]
    confidence = max(0.5, min(0.95, 0.7 + (len(indicators) * 0.05)))
    
    # More indicators = higher threat level (simplified logic)
    threat_index = min(3, len(indicators) // 2)
    
    result = {
        "threat_level": threat_levels[threat_index],
        "confidence_score": confidence,
        "threat_vectors": [ind["type"] for ind in indicators[:3]],
        "recommended_actions": [
            "Increase monitoring of affected systems",
            "Update security protocols",
            "Brief security personnel"
        ],
        "model_version": MODEL_REGISTRY[model_type]["version"]
    }
    
    return result

def predict_network_intrusion(data: Dict[str, Any]) -> Dict[str, Any]:
    """Simulated prediction for network intrusion detection"""
    model_type = "network_intrusion"
    
    if not MODEL_REGISTRY[model_type]["loaded"]:
        load_model(model_type)
        
    # Extract network data
    network_flows = data.get("network_flows", [])
    timespan = data.get("timespan", 3600)  # Default 1 hour
    
    # Simulated processing
    anomaly_threshold = 0.75
    has_anomalies = len(network_flows) > 5  # Simplified check
    
    # Generate random anomaly scores between 0.6 and 0.9
    anomaly_scores = [0.6 + (np.random.rand() * 0.3) for _ in range(min(len(network_flows), 10))]
    
    # Detected anomalies where score > threshold
    detected_anomalies = [
        {
            "flow_id": f"flow-{i}",
            "score": score,
            "source_ip": flow.get("source_ip", "unknown"),
            "destination_ip": flow.get("destination_ip", "unknown"),
            "timestamp": flow.get("timestamp", datetime.utcnow().isoformat())
        }
        for i, (flow, score) in enumerate(zip(network_flows[:10], anomaly_scores))
        if score > anomaly_threshold
    ]
    
    result = {
        "intrusion_detected": has_anomalies and len(detected_anomalies) > 0,
        "confidence_score": max(anomaly_scores) if anomaly_scores else 0.5,
        "anomalies_detected": detected_anomalies,
        "model_version": MODEL_REGISTRY[model_type]["version"]
    }
    
    return result

# Main prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        # Get prediction request
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Extract required fields
        prediction_type = data.get("prediction_type")
        input_data = data.get("input_data", {})
        request_id = data.get("request_id", str(uuid.uuid4()))
        
        if not prediction_type:
            return jsonify({"error": "prediction_type is required"}), 400
            
        # Log the request
        logger.info(f"Prediction request received: {request_id}, type: {prediction_type}")
        
        # Check if we support this prediction type
        if prediction_type not in MODEL_REGISTRY:
            return jsonify({
                "error": f"Unsupported prediction type: {prediction_type}",
                "supported_types": list(MODEL_REGISTRY.keys())
            }), 400
            
        # Process based on prediction type
        start_time = time.time()
        
        try:
            if prediction_type == "threat_assessment":
                result = predict_threat_assessment(input_data)
            elif prediction_type == "network_intrusion":
                result = predict_network_intrusion(input_data)
            else:
                # Generic simulation for other types
                # In production, we would call the appropriate model
                confidence = np.random.uniform(0.65, 0.95)
                result = {
                    "prediction": "Simulated prediction",
                    "confidence_score": confidence,
                    "model_version": MODEL_REGISTRY[prediction_type]["version"]
                }
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return jsonify({
                "error": "Prediction failed",
                "message": str(e),
                "request_id": request_id
            }), 500
            
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            "request_id": request_id,
            "prediction_type": prediction_type,
            "result": result,
            "processing_time_ms": int(processing_time * 1000),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Prediction completed: {request_id}, time: {processing_time:.2f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Unhandled exception in predict endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    gpu_info = "not available"
    
    if torch.cuda.is_available():
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "count": torch.cuda.device_count(),
            "memory": {
                "allocated": f"{torch.cuda.memory_allocated(0) / 1024**2:.2f} MB",
                "reserved": f"{torch.cuda.memory_reserved(0) / 1024**2:.2f} MB"
            }
        }
        
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": sum(1 for m in MODEL_REGISTRY.values() if m["loaded"]),
        "total_models": len(MODEL_REGISTRY),
        "gpu": gpu_info
    })

# Model status endpoint
@app.route('/models', methods=['GET'])
def list_models():
    """List available models and their status"""
    models = []
    
    for model_type, info in MODEL_REGISTRY.items():
        models.append({
            "type": model_type,
            "name": info["name"],
            "version": info["version"],
            "model_type": info["type"],
            "loaded": info["loaded"]
        })
        
    return jsonify({
        "models": models,
        "count": len(models),
        "device": device
    })

# Preload specific models on startup if needed
@app.before_first_request
def preload_models():
    """Preload frequently used models"""
    try:
        # Load the most commonly used models
        priority_models = ["threat_assessment", "network_intrusion"]
        
        for model_type in priority_models:
            logger.info(f"Preloading model: {model_type}")
            load_model(model_type)
            
    except Exception as e:
        logger.error(f"Error preloading models: {str(e)}")

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 