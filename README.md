# Lymeric Materials Platform

A comprehensive materials informatics platform for polymer discovery, combining ML-powered predictions with advanced data management.

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker Desktop installed and running
- 8GB RAM minimum
- 10GB free disk space

### One-Command Start

```bash
git clone <repository-url>
cd lymeric-platform
docker compose up -d
```

**That's it!** The platform will be available at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📋 What's Included

### ✅ Advanced Features (Newly Deployed)

1. **User Authentication** - JWT-based auth with bcrypt password hashing
2. **Substructure Search** - RDKit-powered chemical structure search
3. **ML Model Training UI** - Train models with Optuna and AutoGluon

### Core Platform Features

- **Data Management** - PostgreSQL database with materials schema
- **CSV/Excel Upload** - Batch import with validation
- **Data Quality Dashboard** - Completeness analysis and outlier detection
- **Interactive Visualizations** - Correlation matrices and scatter plots
- **ML Predictions** - Ensemble models for polymer properties
- **Research Assistant** - AI-powered chat for materials science queries

---

## 🔧 Detailed Setup

### Option 1: Docker (Recommended)

**Start all services:**
```bash
docker compose up -d postgres redis data-platform-backend
```

**View logs:**
```bash
docker logs lymeric-data-backend --tail 50 -f
```

**Stop services:**
```bash
docker compose down
```

### Option 2: Local Development

**Backend:**
```bash
cd packages/data-platform/backend

# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd packages/data-platform/frontend
npm install
npm run dev
```

---

## 🧪 Testing the Features

### 1. User Authentication

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123"}'
```

Or visit: http://localhost:3000/register

**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "email": "test@example.com"
}
```

### 2. Substructure Search

**Search for benzene rings:**
```bash
curl -X POST http://localhost:8000/api/search/substructure \
  -H "Content-Type: application/json" \
  -d '{"query_smiles":"c1ccccc1","limit":10}'
```

Or visit: http://localhost:3000/search and enter `c1ccccc1`

### 3. ML Model Training

**Start a training job:**
```bash
curl -X POST http://localhost:8000/api/train/start \
  -H "Content-Type: application/json" \
  -d '{
    "property": "tg",
    "method": "basic",
    "n_estimators": 100
  }'
```

Or visit: http://localhost:3000/training

---

## 🐛 Troubleshooting

### Backend Won't Start

**Problem:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
# Rebuild Docker image
docker compose build data-platform-backend

# Check logs for specific error
docker logs lymeric-data-backend --tail 100
```

### Database Connection Failed

**Problem:** `FATAL: role "lymeric_user" does not exist`

**Solution:**
```bash
# Restart PostgreSQL with volume reset
docker compose down -v
docker compose up -d postgres
sleep 5
docker compose up -d data-platform-backend
```

### Frontend Can't Connect to Backend

**Problem:** "Failed to fetch" errors in browser

**Check:**
1. Backend is running: `curl http://localhost:8000/`
2. CORS is configured: Check `packages/data-platform/backend/app/core/config.py`
3. Frontend API URL: Should be `http://localhost:8000` in `.env.local`

### Port Already in Use

**Problem:** `port is already allocated`

**Solution:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

---

## 📦 Docker Configuration

### Services

| Service | Port | Purpose |
|---------|------|---------|
| `postgres` | 5432 | PostgreSQL 16 database |
| `redis` | 6379 | Caching and task queue |
| `data-platform-backend` | 8000 | FastAPI backend |
| `data-platform-frontend` | 3000 | Next.js frontend (optional) |

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://lymeric_user:lymeric_password@postgres:5432/lymeric_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-this-in-production

# API Keys (optional)
ANTHROPIC_API_KEY=your-anthropic-api-key
```

---

## 🔑 Key Dependencies

### Backend (Python 3.11)

- **FastAPI 0.115.0** - Web framework
- **SQLAlchemy 2.0.35** - ORM
- **RDKit 2024.3.5** - Chemistry toolkit
- **bcrypt 4.0.1** - Password hashing (version pinned!)
- **scikit-learn <1.4.1** - ML (AutoGluon compatibility)
- **numpy <1.29** - Array operations (AutoGluon compatibility)
- **Optuna 4.1.0** - Hyperparameter optimization
- **AutoGluon 1.1.1** - AutoML

### Frontend (Node 20+)

- **Next.js 14** - React framework
- **Tailwind CSS** - Styling
- **Recharts** - Visualizations

---

## 📚 Documentation

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Implementation Plan:** `docs/IMPLEMENTATION_PLAN.md`
- **Deployment Guide:** `docs/guides/DEPLOYMENT_GUIDE.md`
- **Quick Start:** `QUICKSTART.md`

---

## 🏗️ Project Structure

```
lymeric-platform/
├── packages/
│   ├── data-platform/
│   │   ├── backend/          # FastAPI backend
│   │   │   ├── app/
│   │   │   │   ├── api/      # API endpoints
│   │   │   │   ├── models/   # SQLAlchemy models
│   │   │   │   ├── services/ # Business logic
│   │   │   │   └── core/     # Configuration
│   │   │   ├── Dockerfile
│   │   │   └── requirements.txt
│   │   └── frontend/         # Next.js frontend
│   │       ├── app/          # Pages and components
│   │       ├── Dockerfile
│   │       └── package.json
│   ├── ai-services/          # ML prediction services
│   └── research-assistant/   # AI chat interface
├── docker-compose.yml
└── README.md
```

---

## ⚠️ Important Notes

### Dependency Version Constraints

**CRITICAL:** The following versions are pinned for compatibility:

- `bcrypt==4.0.1` - Newer versions break passlib
- `scikit-learn<1.4.1` - AutoGluon requires <1.4.1
- `numpy<1.29` - AutoGluon requires <1.29

**DO NOT** upgrade these without testing thoroughly!

### Disabled Features

- **Molecule Visualization API** (`/api/molecule`) is temporarily disabled
- Requires X11 libraries (libxrender, libexpat, etc.) in Docker
- Can be re-enabled by uncommenting in `app/main.py` and installing X11 deps

### Production Deployment

Before deploying to production:

1. **Change `SECRET_KEY`** in environment variables
2. **Use proper password** for PostgreSQL
3. **Enable HTTPS** with reverse proxy (nginx/traefik)
4. **Set `DEBUG=False`** in backend config
5. **Use managed database** (AWS RDS, etc.)
6. **Add monitoring** (Prometheus, Grafana)

---

## 🎯 Next Steps

1. **Add Sample Data:** Import materials via `/upload` page
2. **Train Your First Model:** Use the training UI with your data
3. **Explore Visualizations:** Check data quality and correlations
4. **Customize:** Modify models, add properties, extend features

---

## 🤝 Contributing

This platform is designed for extensibility:

- Add new ML models in `packages/ai-services/`
- Create custom API endpoints in `packages/data-platform/backend/app/api/`
- Build new frontend pages in `packages/data-platform/frontend/app/`

---

## 📄 License

[Your License Here]

---

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review `docker logs lymeric-data-backend`
3. Verify environment variables in `.env`
4. Ensure Docker has sufficient resources (8GB RAM minimum)

---

**Built with ❤️ for materials science researchers**
