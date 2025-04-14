from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import httpx
import json
import time
from datetime import datetime, timedelta
import uuid
import asyncio

from core.config import settings
from core.security import verify_token
from core.logging import get_request_logger

router = APIRouter()
logger = get_request_logger()

# Sample prediction types based on national security operations
PREDICTION_TYPES = [
    "threat_assessment",
    "network_intrusion",
    "social_media_analysis",
    "geopolitical_risk",
    "infrastructure_vulnerability",
    "resource_allocation",
    "disinformation_detection",
    "behavioral_anomaly"
]

# Mock data storage - would be replaced with database in production
predictions_store = []

# Request and response models
class PredictionRequest(BaseModel):
    prediction_type: str = Field(..., description="Type of prediction to generate")
    input_data: Dict[str, Any] = Field(..., description="Input data for prediction")
    source_systems: List[str] = Field(default_factory=list, description="Source systems for the data")
    priority: int = Field(1, ge=1, le=5, description="Priority level (1-5)")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class PredictionResponse(BaseModel):
    id: str
    prediction_type: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    source_systems: List[str]
    tags: List[str]
    priority: int
    blockchain_verification: Optional[Dict[str, Any]] = None

class PredictionListResponse(BaseModel):
    predictions: List[PredictionResponse]
    total: int
    page: int
    page_size: int

# Authentication dependency
async def get_current_user(request: Request):
    # In a real application, extract and verify the token from the Authorization header
    # For this demo, we'll return a simulated user
    return {
        "id": "user-001",
        "username": "john.analyst",
        "role": "analyst",
        "security_clearance": "top_secret"
    }

# Background task for processing predictions
async def process_prediction(prediction_id: str, prediction_type: str, input_data: Dict[str, Any], 
                      priority: int, user_id: str):
    """
    Process a prediction request asynchronously
    In a real app, this would call ML models or external services
    """
    # Simulate processing time based on priority
    processing_time = max(10, 30 - (priority * 5))
    start_time = time.time()
    
    logger.info(
        f"Starting prediction processing",
        extra={
            "prediction_id": prediction_id,
            "prediction_type": prediction_type,
            "user_id": user_id,
            "priority": priority
        }
    )
    
    try:
        # Simulate processing delay
        await asyncio.sleep(processing_time / 10)  # Reduced for demo purposes
        
        # Generate a simulated result based on prediction type
        result = generate_mock_prediction(prediction_type, input_data)
        
        end_time = time.time()
        processing_time_ms = int((end_time - start_time) * 1000)
        
        # Update the prediction in our store
        for pred in predictions_store:
            if pred["id"] == prediction_id:
                pred["status"] = "completed"
                pred["completed_at"] = datetime.utcnow().isoformat()
                pred["result"] = result["result"]
                pred["confidence_score"] = result["confidence_score"]
                pred["processing_time_ms"] = processing_time_ms
                
                # Add blockchain verification (simulated)
                pred["blockchain_verification"] = {
                    "transaction_id": f"tx-{uuid.uuid4()}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "hash": f"0x{uuid.uuid4().hex}",
                    "verified": True
                }
                break
                
        logger.info(
            f"Completed prediction processing",
            extra={
                "prediction_id": prediction_id,
                "processing_time_ms": processing_time_ms,
                "user_id": user_id,
                "confidence_score": result["confidence_score"]
            }
        )
                
    except Exception as e:
        logger.error(
            f"Error processing prediction",
            extra={
                "prediction_id": prediction_id,
                "error": str(e),
                "user_id": user_id
            },
            exc_info=e
        )
        
        # Update prediction with error status
        for pred in predictions_store:
            if pred["id"] == prediction_id:
                pred["status"] = "failed"
                pred["completed_at"] = datetime.utcnow().isoformat()
                pred["result"] = {"error": str(e)}
                break

def generate_mock_prediction(prediction_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate mock prediction results based on type"""
    if prediction_type == "threat_assessment":
        return {
            "result": {
                "threat_level": "medium",
                "threat_vectors": ["cyber", "physical"],
                "recommended_actions": [
                    "Increase network monitoring",
                    "Review access controls"
                ],
                "time_sensitivity": "48 hours",
                "impacted_assets": ["database-cluster-03", "api-gateway-north"]
            },
            "confidence_score": 0.87
        }
    elif prediction_type == "network_intrusion":
        return {
            "result": {
                "intrusion_detected": True,
                "attack_pattern": "APT29-like",
                "source_indicators": ["45.x.x.x", "62.x.x.x"],
                "affected_systems": ["auth-server", "file-storage"],
                "data_exfiltration": {
                    "detected": True,
                    "volume_estimate": "2.3GB"
                },
                "timeline": {
                    "initial_access": "2023-11-02T14:23:15Z",
                    "lateral_movement": "2023-11-03T02:45:09Z"
                }
            },
            "confidence_score": 0.91
        }
    elif prediction_type == "geopolitical_risk":
        return {
            "result": {
                "risk_level": "elevated",
                "regions": ["Eastern Europe", "South China Sea"],
                "factors": [
                    "Political instability",
                    "Resource competition",
                    "Military activity"
                ],
                "projected_timeline": "3-6 months",
                "impact_areas": ["supply chain", "cyber infrastructure", "diplomatic channels"]
            },
            "confidence_score": 0.78
        }
    else:
        # Generic result for other prediction types
        return {
            "result": {
                "prediction": "Analysis complete",
                "findings": [
                    "Pattern #1 detected with 83% confidence",
                    "Temporal correlation with event series E-2043",
                    "Recommended follow-up: human analysis"
                ],
                "related_entities": ["entity-239", "entity-3092", "entity-1204"]
            },
            "confidence_score": 0.82
        }

# Routes
@router.post("", response_model=PredictionResponse)
async def create_prediction(
    request: Request,
    background_tasks: BackgroundTasks,
    prediction_request: PredictionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new prediction task"""
    
    # Validate prediction type
    if prediction_request.prediction_type not in PREDICTION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prediction type. Must be one of: {', '.join(PREDICTION_TYPES)}"
        )
    
    # Generate prediction ID
    prediction_id = f"pred-{uuid.uuid4()}"
    
    # Create prediction record
    prediction = {
        "id": prediction_id,
        "prediction_type": prediction_request.prediction_type,
        "input_data": prediction_request.input_data,
        "source_systems": prediction_request.source_systems,
        "tags": prediction_request.tags,
        "priority": prediction_request.priority,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "created_by": current_user["id"],
        "completed_at": None,
        "result": None,
        "confidence_score": None,
        "processing_time_ms": None,
        "blockchain_verification": None
    }
    
    # Add to store
    predictions_store.append(prediction)
    
    # Log the request
    logger.info(
        f"Prediction request received",
        extra={
            "prediction_id": prediction_id,
            "prediction_type": prediction_request.prediction_type,
            "user_id": current_user["id"],
            "priority": prediction_request.priority
        }
    )
    
    # Process in background
    background_tasks.add_task(
        process_prediction,
        prediction_id,
        prediction_request.prediction_type,
        prediction_request.input_data,
        prediction_request.priority,
        current_user["id"]
    )
    
    return prediction

@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    request: Request,
    status: Optional[str] = None,
    prediction_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    current_user: Dict = Depends(get_current_user)
):
    """List predictions with optional filters"""
    # Apply filters
    filtered_predictions = predictions_store
    
    if status:
        filtered_predictions = [p for p in filtered_predictions if p["status"] == status]
        
    if prediction_type:
        filtered_predictions = [p for p in filtered_predictions if p["prediction_type"] == prediction_type]
    
    # Sort by created_at descending
    filtered_predictions = sorted(filtered_predictions, key=lambda p: p["created_at"], reverse=True)
    
    # Calculate pagination
    total = len(filtered_predictions)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_predictions = filtered_predictions[start_idx:end_idx]
    
    return {
        "predictions": paginated_predictions,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    request: Request,
    prediction_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get a specific prediction by ID"""
    for prediction in predictions_store:
        if prediction["id"] == prediction_id:
            return prediction
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Prediction not found"
    )

@router.post("/{prediction_id}/verify")
async def verify_prediction_integrity(
    request: Request,
    prediction_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Verify the integrity of a prediction using blockchain"""
    # Find the prediction
    prediction = None
    for p in predictions_store:
        if p["id"] == prediction_id:
            prediction = p
            break
            
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
        
    # Check if the prediction has been completed
    if prediction["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed predictions can be verified"
        )
        
    # Simulate blockchain verification
    verification_result = {
        "verified": True,
        "blockchain_reference": prediction.get("blockchain_verification", {}).get("transaction_id", "unknown"),
        "verification_time": datetime.utcnow().isoformat(),
        "verifier": current_user["id"]
    }
    
    logger.info(
        f"Prediction verification performed",
        extra={
            "prediction_id": prediction_id,
            "user_id": current_user["id"],
            "verification_result": verification_result["verified"]
        }
    )
    
    return verification_result 