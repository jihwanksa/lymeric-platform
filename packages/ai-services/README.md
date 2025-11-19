# AI Services Package - Polymer Property Prediction

Machine learning models for predicting polymer properties from SMILES.

## Model

**v85 Random Forest Ensemble** - 1st place Kaggle solution
- **Score**: 0.07533 (Private leaderboard)
- **Features**: 21 chemistry features extracted from SMILES
- **Properties**: Tg, FFV, Tc, Density, Rg

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Predictor Service

```python
from predictor import get_predictor

# Get global predictor instance
predictor = get_predictor()

# Make prediction
predictions = predictor.predict("c1ccccc1")  # Benzene

# Result:
# {
#     'tg': {'value': 5.5, 'confidence': 0.85},
#     'ffv': {'value': 0.35, 'confidence': 0.85},
#     ...
# }
```

## Model Location

Place the trained model at: `packages/ai-services/models/random_forest_v85_best.pkl`

To copy from open_polymer:
```bash
cp /Users/jihwan/Downloads/open_polymer/models/random_forest_v85_best.pkl \
   packages/ai-services/models/
```

## Features Extracted

The predictor automatically extracts 21 features from SMILES:

**Simple Features (10):**
- smiles_length, carbon_count, nitrogen_count, oxygen_count, sulfur_count
- fluorine_count, ring_count, double_bond_count, triple_bond_count, branch_count

**Chemistry Features (11):**
- num_side_chains, backbone_carbons, branching_ratio, aromatic_count
- h_bond_donors, h_bond_acceptors, num_rings, single_bonds
- halogen_count, heteroatom_count, mw_estimate

## Notes

- Tg predictions include transformation: `(9/5) * Tg + 45`
- Confidence scores are currently simplified (0.85 for all)
- Model requires joblib, scikit-learn, numpy
