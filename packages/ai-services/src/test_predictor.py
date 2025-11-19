"""Test script for predictor service"""
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "data-platform" / "backend"))
sys.path.insert(0, str(Path(__file__).parent))

from predictor import PolymerPredictor
from app.services.chemistry_service import ChemistryService

def test_predictor():
    """Test predictor with sample SMILES"""
    print("🧪 Testing Polymer Predictor\n")
    
    # Test SMILES
    test_cases = [
        ("Benzene", "c1ccccc1"),
        ("Ethanol", "CCO"),
        ("Polystyrene repeat", "C(C)c1ccccc1"),
    ]
    
    predictor = PolymerPredictor()
    
    for name, smiles in test_cases:
        print(f"Testing: {name} ({smiles})")
        
        # Validate SMILES
        is_valid = ChemistryService.validate_smiles(smiles)
        print(f"  Valid SMILES: {is_valid}")
        
        if not is_valid:
            continue
        
        # Extract features
        features = predictor.extract_features(smiles)
        if features is not None:
            print(f"  Features extracted: {features.shape}")
        
        # Make predictions
        predictions = predictor.predict(smiles)
        print(f"  Predictions:")
        for prop, result in predictions.items():
            print(f"    {prop}: {result['value']:.3f} (confidence: {result['confidence']:.2f})")
        
        print()

if __name__ == "__main__":
    test_predictor()
