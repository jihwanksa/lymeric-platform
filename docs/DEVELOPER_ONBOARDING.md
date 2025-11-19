# Developer Onboarding Guide

**Welcome to the Lymeric Platform Development Team!**

---

## Project Overview

Lymeric is a monorepo with 3 main packages:
1. **data-platform** - Main FastAPI + Next.js application
2. **research-assistant** - ChatAPI backend with Claude integration
3. **ai-services** - ML prediction service

---

## Development Setup (Mac)

### Prerequisites
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install python@3.13 node@20 postgresql@15 docker
```

### Quick Start
```bash
# Clone repository
git clone https://github.com/jihwanksa/lymeric-platform.git
cd lymeric-platform

# Start services (one command!)
./scripts/start_dev.sh
```

**Services Started:**
- PostgreSQL: `localhost:5432`
- Data Platform Backend: `localhost:8000`
- Research Assistant Backend: `localhost:8001`
- Frontend: `localhost:3000`

### Manual Setup (if script fails)

**1. Database:**
```bash
# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb lymeric

# Or use Docker
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=lymeric \
  postgres:15-alpine
```

**2. Data Platform Backend:**
```bash
cd packages/data-platform/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --port 8000
```

**3. Research Assistant Backend:**
```bash
cd packages/research-assistant/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --port 8001
```

**4. Frontend:**
```bash
cd packages/data-platform/frontend

# Install dependencies
npm install

# Run
npm run dev
```

---

## Project Structure

```
lymeric-platform/
├── packages/
│   ├── data-platform/
│   │   ├── backend/
│   │   │   ├── app/
│   │   │   │   ├── api/          # API endpoints
│   │   │   │   ├── core/         # Config, database
│   │   │   │   ├── models/       # SQLAlchemy models
│   │   │   │   ├── services/     # Business logic
│   │   │   │   └── main.py       # FastAPI app
│   │   │   ├── tests/            # Backend tests
│   │   │   └── requirements.txt
│   │   └── frontend/
│   │       ├── app/              # Next.js pages
│   │       ├── components/       # React components
│   │       └── package.json
│   │
│   ├── research-assistant/
│   │   └── backend/
│   │       ├── app/
│   │       │   ├── api/          # Chat endpoints
│   │       │   ├── models/       # Conversation models
│   │       │   └──services/     # Claude, conversation
│   │       └── conversations.db  # SQLite
│   │
│   └── ai-services/
│       └── src/
│           └── predictor.py      # ML model
│
├── docs/                         # Documentation
├── tests/fixtures/               # Test data
└── scripts/                      # Utility scripts
```

---

## Key Technologies

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **RDKit** - Chemistry toolkit
- **scikit-learn** - ML models
- **Pydantic** - Data validation

### Frontend
- **Next.js 16** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization

### Database
- **PostgreSQL** - Main database (data-platform)
- **SQLite** - Conversation storage (research-assistant)

---

## Common Development Tasks

### Add a New API Endpoint

**1. Create endpoint in `packages/data-platform/backend/app/api/materials.py`:**
```python
@router.get("/search")
def search_materials(query: str, db: Session = Depends(get_db)):
    """Search materials by name or SMILES"""
    results = db.query(Material).filter(
        Material.name.contains(query)
    ).all()
    return results
```

**2. Test it:**
```bash
curl http://localhost:8000/api/materials/search?query=benzene
```

### Add a Frontend Page

**1. Create `packages/data-platform/frontend/app/mypage/page.tsx`:**
```typescript
export default function MyPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold">My Page</h1>
    </div>
  );
}
```

**2. Add to navigation in `app/layout.tsx`:**
```tsx
<a href="/mypage" className="...">
  My Page
</a>
```

**3. Access at:** http://localhost:3000/mypage

### Add a Database Model

**1. Create model in `packages/data-platform/backend/app/models/experiment.py`:**
```python
from sqlalchemy import Column, String, DateTime
from app.core.database import Base

class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(200))
    created_at = Column(DateTime)
```

**2. Create tables:**
```bash
python -c "from app.core.database import engine, Base; from app.models.experiment import Experiment; Base.metadata.create_all(bind=engine)"
```

### Run Tests

```bash
# Backend tests
cd packages/data-platform/backend
pytest

# Specific test file
pytest tests/test_chemistry_service.py

# With coverage
pytest --cov=app tests/
```

---

## Code Style

### Python (Backend)
```python
# Use type hints
def predict_property(smiles: str) -> Dict[str, float]:
    """Predict material properties from SMILES.
    
    Args:
        smiles: SMILES notation string
        
    Returns:
        Dictionary of property predictions
    """
    ...

# Use Pydantic for validation
from pydantic import BaseModel

class MaterialCreate(BaseModel):
    smiles: str
    name: Optional[str] = None
```

### TypeScript (Frontend)
```typescript
// Use interfaces
interface Material {
  id: string;
  smiles: string;
  name?: string;
}

// Use async/await
const fetchMaterials = async (): Promise<Material[]> => {
  const response = await fetch('/api/materials');
  return response.json();
};
```

### Formatting
```bash
# Python (backend)
black app/
isort app/

# TypeScript (frontend)
npm run lint
npm run format
```

---

## Debugging

### Backend
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use print debugging
print(f"Debug: {variable}")

# View logs
tail -f /tmp/backend_lymeric.log
```

### Frontend
```typescript
// Browser console
console.log('Debug:', data);

// React DevTools
// Install browser extension

// View logs
tail -f /tmp/frontend_lymeric.log
```

### Database
```bash
# Connect to PostgreSQL
psql lymeric

# List tables
\dt

# Query
SELECT * FROM materials LIMIT 5;

# View SQLite (conversations)
sqlite3 packages/research-assistant/backend/conversations.db
.tables
SELECT * FROM conversations;
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add my feature

- Detailed description
- Why this change
- Related issues"

# Push and create PR
git push origin feature/my-feature

# After review, merge to main
git checkout main
git pull
git merge feature/my-feature
git push
```

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

---

## Environment Variables

### Development .env
```bash
# Data Platform Backend
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lymeric
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:3000

# Research Assistant Backend
ANTHROPIC_API_KEY=sk-ant-xxx  # Optional for mock mode
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## API Documentation

**Auto-generated docs:**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

**Test endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# List materials
curl http://localhost:8000/api/materials

# Add material
curl -X POST http://localhost:8000/api/materials \
  -H "Content-Type: application/json" \
  -d '{"smiles":"c1ccccc1","name":"Benzene"}'
```

---

## Troubleshooting

### "Module not found" Error
```bash
# Verify virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -l

# Verify DATABASE_URL
echo $DATABASE_URL

# Restart PostgreSQL
brew services restart postgresql@15
```

### Frontend Not Loading
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall node_modules
rm -rf node_modules
npm install

# Restart dev server
npm run dev
```

### Port Already in Use
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

---

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution

### Integration Tests
- Test API endpoints
- Use test database
- Realistic scenarios

### E2E Tests (Future)
- Browser automation
- Full user workflows
- Staging environment

---

## Performance Tips

### Backend
```python
# Use database indexes
class Material(Base):
    smiles = Column(String, index=True)

# Batch operations
db.bulk_insert_mappings(Material, data)

# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_calculation(smiles: str):
    ...
```

### Frontend
```typescript
// Lazy load components
const HeavyComponent = dynamic(() => import('./HeavyComponent'));

// Memoize expensive computations
const memoizedValue = useMemo(() => computeExpensive(data), [data]);

// Debounce user input
const debouncedSearch = debounce(search, 300);
```

---

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production deployment.

---

## Resources

**Documentation:**
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [RDKit Docs](https://www.rdkit.org/docs/)

**Code Examples:**
- `tests/fixtures/sample_materials.csv` - Example data
- `tests/test_chemistry_service.py` - Backend tests
- `docs/` - All project documentation

**Team Communication:**
- GitHub Issues - Bug reports, features
- Pull Requests - Code reviews
- Discussions - Design decisions

---

## Next Steps

**Week 1:**
- [ ] Complete environment setup
- [ ] Read all documentation
- [ ] Run all tests successfully
- [ ] Make a small code change and test

**Week 2:**
- [ ] Add a new API endpoint
- [ ] Create a new frontend page
- [ ] Fix a small bug
- [ ] Write tests for your changes

**Week 3:**
- [ ] Implement a complete feature
- [ ] Review teammates' PRs
- [ ] Improve documentation
- [ ] Optimize performance

---

**Welcome to the team!** 🚀
