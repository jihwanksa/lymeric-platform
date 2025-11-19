# ML Model Integration - Analysis & Fixes

## Problem Identified

The predictor was returning 0.00 for all predictions because the model structure didn't match expectations.

## Root Cause Analysis

By analyzing [`train_v85_best.py`](file:///Users/jihwan/Downloads/open_polymer/src/train_v85_best.py), I found:

### Actual Model Structure (from training code)

```python
# Line 189-194: Model is saved as dict
pickle.dump({
    'models': self.models,      # Dict: {prop_name: [model1, model2, model3, model4, model5]}
    'scalers': self.scalers,    # Dict: {prop_name: StandardScaler}
    'n_ensemble': self.n_ensemble,  # 5
    'feature_names': self.feature_names
}, f)
```

**Key points:**
- Top level is a **dict** with 4 keys
- `models[property]` is a **list of 5 RandomForest models** (ensemble)
- `scalers[property]` is a **StandardScaler** object
- Need **ensemble averaging** - predict with all 5 models and take mean

### Our Original Predictor (Wrong)

```python
# ❌ Assumed single model per property
model = self.models[prop]
pred = model.predict(features)[0]
```

## Fixes Applied

### 1. Fixed `load_model()` method

**Before:** Used `joblib.load()` directly  
**After:** Properly extract dict structure

```python
data = pickle.load(f)
self.models = data.get('models', {})      # Extract models dict
self.scalers = data.get('scalers', {})    # Extract scalers dict
self.n_ensemble = data.get('n_ensemble', 5)
```

### 2. Fixed `predict()` method

**Before:** Single model prediction  
**After:** Ensemble averaging with scaling

```python
# Get scaler and ensemble models
scaler = self.scalers[prop]
ensemble_models = self.models[prop]  # List of 5 models

# Scale features with StandardScaler
features_scaled = scaler.transform(features)

# Ensemble prediction: average of all 5 models
ensemble_preds = np.array([
    model.predict(features_scaled)[0] 
    for model in ensemble_models
])
pred = ensemble_preds.mean()
```

### 3. Added Confidence Scoring

```python
# Confidence based on ensemble variance
# Lower variance = more agreement = higher confidence
confidence = 1.0 / (1.0 + ensemble_preds.std())
confidence = min(max(confidence, 0.0), 1.0)  # Clamp [0, 1]
```

### 4. Fixed Property Names

**Before:** `['tg', 'ffv', 'tc', 'density', 'rg']` (lowercase)  
**After:** `['Tg', 'FFV', 'Tc', 'Density', 'Rg']` (capital - matches training)

### 5. Correct Tg Transformation

```python
if prop == 'Tg':  # Capital T
    pred = (9/5) * pred + 45  # From 2nd place discovery
```

## Testing Plan (After Model Retraining)

Once you copy the new model file, test:

```bash
cd /Users/jihwan/Downloads/lymeric-platform/packages/ai-services/src
cd ../../data-platform/backend && source venv/bin/activate && cd -
python test_predictor.py
```

Expected output:
- ✅ Model loads with no errors
- ✅ Properties loaded: ['Tg', 'FFV', 'Tc', 'Density', 'Rg']
- ✅ Non-zero predictions for each property
- ✅ Confidence scores between 0.0 and 1.0

## Files Modified

- [`predictor.py`](file:///Users/jihwan/Downloads/lymeric-platform/packages/ai-services/src/predictor.py) - Fixed model loading and prediction
- Pushed to GitHub (commit: ad21b2a)

## Next Steps

1. ⏳ **Wait for model training to complete**
2. Copy new model file: `random_forest_v53_best.pkl` → `packages/ai-services/models/`
3. Test predictor with real model
4. Test API endpoint: `POST /api/predictions`
5. Test frontend predictions page
6. Deploy and celebrate! 🎉
