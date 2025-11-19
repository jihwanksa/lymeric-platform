"""Predictor service using v85 Random Forest model

This service loads the trained v85 model and provides prediction functionality
for polymer properties (Tg, FFV, Tc, Density, Rg) based on SMILES input.
"""
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "data-platform" / "backend"))

from app.services.chemistry_service import ChemistryService


class PolymerPredictor:
    """Predictor for polymer properties using v85 Random Forest ensemble"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize predictor with trained model
        
        Args:
            model_path: Path to trained model pickle file. If None, uses default location.
        """
        if model_path is None:
            # Try v85 first, then v53 (actual filename may vary)
            model_dir = Path(__file__).parent.parent / "models"
            possible_models = [
                model_dir / "random_forest_v85_best.pkl",
                model_dir / "random_forest_v53_best.pkl",
            ]
            for path in possible_models:
                if path.exists():
                    model_path = path
                    break
            else:
                model_path = model_dir / "random_forest_v85_best.pkl"  # Default
        
        self.model_path = Path(model_path)
        self.models = None
        self.scalers = {}  # Scalers for each property
        self.n_ensemble = 5  # Number of models in ensemble
        self.property_names = ['Tg', 'FFV', 'Tc', 'Density', 'Rg']  # Use capital names from training
        self.feature_names = None
        
        # Load model if it exists
        if self.model_path.exists():
            self.load_model()
        else:
            print(f"Warning: Model not found at {self.model_path}")
            print("Predictions will return placeholder values.")
    
    def load_model(self):
        """Load the trained model from disk"""
        try:
            # Load pickle file
            import pickle
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            
            # Extract models and scalers from dict structure
            # Structure: {'models': {prop: [model1, model2, ...], ...}, 'scalers': {prop: scaler, ...}}
            if isinstance(data, dict):
                self.models = data.get('models', {})
                self.scalers = data.get('scalers', {})
                self.n_ensemble = data.get('n_ensemble', 5)
                self.feature_names = data.get('feature_names')
            else:
                # Fallback: assume it's the models dict directly
                self.models = data
                self.scalers = {}
            
            print(f"✅ Loaded v85 model from {self.model_path}")
            print(f"   Properties loaded: {list(self.models.keys())}")
            print(f"   Ensemble size: {self.n_ensemble}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.models = None
            self.scalers = {}
    
    def extract_features(self, smiles: str) -> Optional[np.ndarray]:
        """Extract 21 features from SMILES
        
        Args:
            smiles: SMILES string
            
        Returns:
            numpy array of 21 features, or None if extraction fails
        """
        features_dict = ChemistryService.extract_all_features(smiles)
        if features_dict is None:
            return None
        
        # Convert to ordered array (must match training order)
        feature_order = [
            # Simple features (10)
            'smiles_length', 'carbon_count', 'nitrogen_count', 'oxygen_count',
            'sulfur_count', 'fluorine_count', 'ring_count', 'double_bond_count',
            'triple_bond_count', 'branch_count',
            # Chemistry features (11)
            'num_side_chains', 'backbone_carbons', 'branching_ratio',
            'aromatic_count', 'h_bond_donors', 'h_bond_acceptors',
            'num_rings', 'single_bonds', 'halogen_count',
            'heteroatom_count', 'mw_estimate'
        ]
        
        try:
            features = np.array([features_dict[f] for f in feature_order])
            return features.reshape(1, -1)  # Shape: (1, 21)
        except KeyError as e:
            print(f"Missing feature: {e}")
            return None
    
    def predict(self, smiles: str) -> Dict[str, Dict[str, float]]:
        """Predict all properties for a SMILES string
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dict with predictions for each property:
            {
                'tg': {'value': float, 'confidence': float},
                'ffv': {'value': float, 'confidence': float},
                ...
            }
        """
        # Validate SMILES
        if not ChemistryService.validate_smiles(smiles):
            return self._placeholder_predictions()
        
        # Extract features
        features = self.extract_features(smiles)
        if features is None:
            return self._placeholder_predictions()
        
        # If model not loaded, return placeholders
        if self.models is None:
            return self._placeholder_predictions()
        
        # Make predictions
        predictions = {}
        for prop in self.property_names:
            try:
                # Check if property has models and scalers
                if prop not in self.models or prop not in self.scalers:
                    predictions[prop] = {'value': 0.0, 'confidence': 0.0}
                    continue
                
                # Get scaler and ensemble models
                scaler = self.scalers[prop]
                ensemble_models = self.models[prop]
                
                # Scale features
                features_scaled = scaler.transform(features)
                
                # Ensemble prediction: average of all models
                ensemble_preds = np.array([
                    model.predict(features_scaled)[0] 
                    for model in ensemble_models
                ])
                pred = ensemble_preds.mean()
                
                # Apply Tg transformation (from 2nd place discovery in v85)
                if prop == 'Tg':
                    pred = (9/5) * pred + 45
                
                # Estimate confidence based on ensemble variance
                confidence = 1.0 / (1.0 + ensemble_preds.std())  # Lower variance = higher confidence
                confidence = min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]
                
                predictions[prop] = {
                    'value': float(pred),
                    'confidence': float(confidence)
                }
                
            except Exception as e:
                print(f"Prediction failed for {prop}: {e}")
                predictions[prop] = {'value': 0.0, 'confidence': 0.0}
        
        return predictions
    
    def _placeholder_predictions(self) -> Dict[str, Dict[str, float]]:
        """Return placeholder predictions when model unavailable"""
        return {
            'tg': {'value': 0.0, 'confidence': 0.0},
            'ffv': {'value': 0.0, 'confidence': 0.0},
            'tc': {'value': 0.0, 'confidence': 0.0},
            'density': {'value': 0.0, 'confidence': 0.0},
            'rg': {'value': 0.0, 'confidence': 0.0}
        }


# Global predictor instance
_predictor = None

def get_predictor() -> PolymerPredictor:
    """Get or create global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = PolymerPredictor()
    return _predictor
