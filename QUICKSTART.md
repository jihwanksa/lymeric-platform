# Quick Start Guide

## Prerequisites

- Docker Desktop installed
- Node.js 18+ installed
- Python 3.10+ installed

## Starting the Application

### Method 1: Quick Start Script (Recommended)

```bash
cd /Users/jihwan/Downloads/lymeric-platform
./scripts/start_dev.sh
```

This will:
1. Start PostgreSQL and Redis in Docker
2. Start backend API on port 8000
3. Start frontend on port 3000

### Method 2: Manual Start

```bash
# 1. Start databases
docker compose up -d postgres redis

# 2. Start backend (Terminal 1)
cd packages/data-platform/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start frontend (Terminal 2)
cd packages/data-platform/frontend
npm run dev
```

## Accessing the Application

Once started, access:

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health
- **PostgreSQL**: `localhost:5432` (user: `lymeric`, password: `lymeric_dev_password`)

## Testing the Platform

### 1. Add a Material

Go to http://localhost:3000/materials and click "Add Material":
- **Name**: Benzene
- **SMILES**: `c1ccccc1`
- Click "Add Material"

The system will automatically:
- Validate SMILES
- Canonicalize it
- Extract 21 chemistry features

### 2. Make Predictions

Go to http://localhost:3000/predictions:
- Enter SMILES: `c1ccccc1`
- Click "Predict Properties"
- See predictions for Tg, FFV, Tc, Density, Rg

### 3. Test API

Visit http://localhost:8000/docs to see interactive API documentation and test endpoints.

## Stopping the Application

```bash
./scripts/stop_dev.sh
```

Or manually:
```bash
# Stop processes
pkill -f "uvicorn app.main"
pkill -f "next dev"

# Stop Docker
docker compose down
```

## Troubleshooting

### "docker-compose: command not found"

Use `docker compose` (space) instead:
```bash
docker compose up -d
```

Or install docker-compose:
```bash
brew install docker-compose
```

### Backend won't start

Check if venv is activated and dependencies installed:
```bash
cd packages/data-platform/backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start

Install dependencies:
```bash
cd packages/data-platform/frontend
npm install
```

### Port already in use

Find and kill the process:
```bash
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:3000 | xargs kill  # Frontend
```

## Logs

Check logs for debugging:
```bash
tail -f /tmp/backend.log   # Backend logs
tail -f /tmp/frontend.log  # Frontend logs
```

## What's Working

✅ **Materials Management**
- Add materials with SMILES
- Automatic validation and canonicalization
- 21 chemistry features auto-extracted
- List and filter materials

✅ **ML Predictions**
- Predict polymer properties from SMILES
- v85 Random Forest model (1st place Kaggle)
- Ensemble averaging (5 models)
- Confidence scores

✅ **Database**
- PostgreSQL with Material schema
- UUID primary keys
- JSONB for flexible features

## Next: Phase 2 Development

Ready to proceed with:
- CSV/Excel upload
- Data quality dashboard
- Visualization components

See `docs/FOUNDATION_SETUP.md` for detailed progress.
