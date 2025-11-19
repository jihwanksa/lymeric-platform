"""Predictions API endpoints - ML model predictions using v85 Random Forest"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
import sys
from pathlib import Path

# Add ai-services to path
ai_services_path = Path(__file__).parent.parent.parent.parent.parent / "ai-services" / "src"
sys.path.insert(0, str(ai_services_path))

try:
    from predictor import get_predictor
    PREDICTOR_AVAILABLE = True
except ImportError:
    PREDICTOR_AVAILABLE = False
    print("Warning: Predictor not available. Install ai-services dependencies.")

router = APIRouter()

class PredictionRequest(BaseModel):
    """Request schema for predictions"""
    smiles: str

class PredictionResponse(BaseModel):
    """Response schema for predictions"""
    smiles: str
    predictions: Dict[str, Dict[str, float]]  # property_name -> {value, confidence}

@router.post("/", response_model=PredictionResponse)
def predict_properties(request: PredictionRequest):
    """Predict polymer properties from SMILES using v85 Random Forest model
    
    The model predicts 5 properties:
    - Tg: Glass transition temperature (°C)
    - FFV: Free volume fraction
    - Tc: Crystallization temperature (°C)
    - Density: Material density (g/cm³)
    - Rg: Radius of gyration (Å)
    
    Features: Automatically extracts 21 chemistry features from SMILES
    """
    if not PREDICTOR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Prediction service unavailable. Please install ai-services dependencies."
        )
    
    try:
        # Get predictor and make predictions
        predictor = get_predictor()
        predictions = predictor.predict(request.smiles)
        
        return {
            "smiles": request.smiles,
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )
