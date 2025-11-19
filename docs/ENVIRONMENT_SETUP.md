# Environment Setup - Lessons Learned

This document captures all the environment issues encountered during development and how they were resolved, so future developers don't waste time on the same problems.

## 🎯 TL;DR - What Works

**Use Docker with these exact versions:**
- Python: 3.11
- bcrypt: 4.0.1
- scikit-learn: <1.4.1
- numpy: <1.29
- AutoGluon: 1.1.1

## 🔥 Issues Encountered & Solutions

### 1. Python 3.13 + bcrypt Incompatibility ❌

**Problem:**
```
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**Root Cause:** Python 3.13 changed module loading behavior, breaking passlib's bcrypt detection.

**Solution:** Downgrade to Python 3.11
```dockerfile
FROM python:3.11-slim
```

### 2. passlib + bcrypt Version Mismatch ❌

**Problem:**
```python
AttributeError: module 'bcrypt' has no attribute '__about__'
```

**Root Cause:** passlib 1.7.4 expects bcrypt <=4.0.1, but pip installs bcrypt 4.2.x by default.

**Solution:** Pin bcrypt version in requirements.txt
```txt
bcrypt==4.0.1
passlib[bcrypt]==1.7.4
```

### 3. numpy 2.x + AutoGluon Incompatibility ❌

**Problem:**
```
ERROR: Cannot install autogluon-tabular 1.1.1 and numpy==2.1.2
autogluon-tabular 1.1.1 depends on numpy<1.29 and >=1.21
```

**Root Cause:** AutoGluon doesn't support numpy 2.x yet.

**Solution:** Constrain numpy version
```txt
numpy<1.29,>=1.23
```

### 4. scikit-learn 1.5.x + AutoGluon Incompatibility ❌

**Problem:**
```
ERROR: Cannot install autogluon-tabular 1.1.1 and scikit-learn==1.5.2
autogluon-tabular 1.1.1 depends on scikit-learn<1.4.1 and >=1.3.0
```

**Root Cause:** AutoGluon hasn't updated for newer scikit-learn APIs.

**Solution:** Constrain scikit-learn version
```txt
scikit-learn<1.4.1,>=1.3.0
```

### 5. RDKit + X11 Libraries in Docker ❌

**Problem:**
```
ImportError: libexpat.so.1: cannot open shared object file
ImportError: libxrender.so.1: cannot open shared object file
```

**Root Cause:** RDKit's molecular drawing (rdMolDraw2D) requires X11 libraries not included in slim Docker images.

**Solution Option 1:** Install X11 libraries
```dockerfile
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    libsm6 \
    libexpat1 \
    libgomp1
```

**Solution Option 2 (Used):** Disable molecule visualization endpoint
```python
# In app/main.py
# from app.api import molecule  # Commented out
# app.include_router(molecule.router, ...)  # Commented out
```

### 6. python-multipart Missing ❌

**Problem:**
```
RuntimeError: Form data requires "python-multipart" to be installed
```

**Root Cause:** FastAPI file upload endpoints need python-multipart, not auto-installed.

**Solution:** Add to requirements.txt
```txt
python-multipart==0.0.12
```

### 7. uvicorn --reload Mode Issues ❌

**Problem:** Backend crashes immediately after starting with --reload

**Root Cause:** Reload mode spawns subprocess with different PYTHONPATH, can't find modules.

**Solution:** Run without --reload in Docker
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Removed: --reload flag
```

## ✅ Final Working Configuration

### requirements.txt
```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
pydantic-settings==2.6.0
bcrypt==4.0.1                    # ← Pinned!
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.12         # ← Required!
email-validator==2.2.0
rdkit==2024.3.5
scikit-learn<1.4.1,>=1.3.0      # ← Constrained!
pandas==2.2.3
numpy<1.29,>=1.23               # ← Constrained!
optuna==4.1.0
autogluon.tabular==1.1.1
```

### Dockerfile
```dockerfile
FROM python:3.11-slim            # ← Python 3.11, not 3.13!

WORKDIR /app

# Install system dependencies for RDKit
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxrender1 \             # ← X11 libraries
    libxext6 \
    libsm6 \
    libexpat1 \
    libgomp1 \
    libxinerama1 \
    libxi6 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# No --reload in production!
```

## 🧪 Verification Steps

### 1. Test bcrypt Works
```bash
docker exec lymeric-data-backend python -c "
from passlib.context import CryptContext
ctx = CryptContext(schemes=['bcrypt'])
print('✅ bcrypt working')
"
```

### 2. Test RDKit Imports
```bash
docker exec lymeric-data-backend python -c "
from rdkit import Chem
print('✅ RDKit working')
"
```

### 3. Test AutoGluon Imports
```bash
docker exec lymeric-data-backend python -c "
from autogluon.tabular import TabularPredictor
print('✅ AutoGluon working')
"
```

### 4. Test Registration Endpoint
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123"}'
# Should return JWT token
```

## 🚫 What NOT To Do

1. **Don't use Python 3.13** - breaks bcrypt/passlib
2. **Don't upgrade bcrypt** - passlib not compatible with 4.1+
3. **Don't upgrade numpy to 2.x** - AutoGluon not compatible
4. **Don't upgrade scikit-learn to 1.4+** - AutoGluon not compatible
5. **Don't use --reload in Docker** - causes import issues
6. **Don't forget python-multipart** - needed for file uploads
7. **Don't skip X11 libraries** - if using RDKit drawing

## 📊 Time Spent on Environment Issues

- Python 3.13 → 3.12: 1 hour
- bcrypt version debugging: 2 hours
- numpy/sklearn conflicts: 1.5 hours
- RDKit X11 libraries: 2 hours
- Miscellaneous (multipart, reload mode): 0.5 hours

**Total:** ~7 hours debugging environment (could have been 5 minutes with this doc!)

## 🎯 Recommendations

1. **Use Docker** - Eliminates host OS differences
2. **Pin ALL versions** - Especially bcrypt, numpy, scikit-learn
3. **Test incrementally** - Add one dependency at a time
4. **Check logs thoroughly** - Don't assume package is installed because pip said so
5. **Use this exact configuration** - It's battle-tested

## 📚 Additional Resources

- [PassLib bcrypt backend docs](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)
- [AutoGluon installation guide](https://auto.gluon.ai/stable/install.html)
- [RDKit in Docker](https://github.com/rdkit/rdkit/tree/master/Docker)

---

**Last Updated:** November 2025  
**Python Version:** 3.11  
**Platform Tested:** macOS (Docker Desktop), Linux (Docker CE)
