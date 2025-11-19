# Deployment Guide - Lymeric Platform

**Production Deployment Checklist**

---

## Prerequisites

- Docker & Docker Compose installed
- Cloud provider account (AWS/GCP/Azure/Render)
- Domain name (optional but recommended)
- PostgreSQL database (managed service)
- Redis instance (for caching)

---

## Step 1: Environment Configuration

Create production `.env` files:

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/lymeric_prod
REDIS_URL=redis://host:6379/0

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxx  # If using real Claude

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Environment
ENVIRONMENT=production
DEBUG=false
```

### Frontend (.env.production)
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## Step 2: Containerization

### Root Dockerfile (Multi-service)
```dockerfile
# Multi-stage build for data-platform backend
FROM python:3.13-slim as backend
WORKDIR /app
COPY packages/data-platform/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY packages/data-platform/backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Research assistant backend
FROM python:3.13-slim as assistant
WORKDIR /app
COPY packages/research-assistant/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY packages/research-assistant/backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

# Frontend
FROM node:20-alpine as frontend
WORKDIR /app
COPY packages/data-platform/frontend/package*.json .
RUN npm ci
COPY packages/data-platform/frontend/ .
RUN npm run build
CMD ["npm", "start"]
```

### docker-compose.production.yml
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      target: backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    restart: always

  assistant:
    build:
      context: .
      target: assistant
    ports:
      - "8001:8001"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: always

  frontend:
    build:
      context: .
      target: frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    restart: always

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=lymeric_prod
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
```

---

## Step 3: Cloud Deployment Options

### Option A: Render (Easiest)

1. **Create Services:**
   - Web Service: Data Platform Backend
   - Web Service: Research Assistant Backend
   - Web Service: Frontend
   - PostgreSQL Database
   - Redis Instance

2. **Connect Repository:**
   ```bash
   # Push to GitHub
   git push origin main
   ```

3. **Deploy Each Service:**
   - Backend: `docker build --target backend`
   - Assistant: `docker build --target assistant`
   - Frontend: `docker build --target frontend`

4. **Set Environment Variables** in Render dashboard

5. **Custom Domain:** Add in Render settings

### Option B: AWS (Full Control)

1. **Set up ECR (Container Registry):**
   ```bash
   aws ecr create-repository --repository-name lymeric-backend
   aws ecr create-repository --repository-name lymeric-frontend
   ```

2. **Build & Push Images:**
   ```bash
   docker build -t lymeric-backend --target backend .
   docker tag lymeric-backend:latest xxx.dkr.ecr.region.amazonaws.com/lymeric-backend:latest
   docker push xxx.dkr.ecr.region.amazonaws.com/lymeric-backend:latest
   ```

3. **Set up RDS PostgreSQL:**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier lymeric-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password yourpassword
   ```

4. **Deploy to ECS/Fargate:**
   - Create ECS cluster
   - Create task definitions
   - Create services
   - Configure load balancer

5. **Set up CloudFront** for frontend CDN

### Option C: Google Cloud Platform

1. **Cloud Run (Serverless):**
   ```bash
   gcloud run deploy lymeric-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Cloud SQL for PostgreSQL:**
   ```bash
   gcloud sql instances create lymeric-db \
     --database-version=POSTGRES_15 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

---

## Step 4: Database Migration

```bash
# Run migrations in production
docker exec -it backend-container alembic upgrade head

# Or manually create tables
docker exec -it backend-container python -c "
from app.core.database import engine, Base
from app.models import material, conversation
Base.metadata.create_all(bind=engine)
"
```

---

## Step 5: CI/CD Pipeline

### GitHub Actions (.github/workflows/deploy.yml)
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t lymeric-backend --target backend .
          docker build -t lymeric-frontend --target frontend .
      
      - name: Push to registry
        run: |
          # Push to your container registry
          
      - name: Deploy to production
        run: |
          # Deploy using your cloud provider CLI
```

---

## Step 6: Monitoring & Logging

### Application Monitoring
```python
# Add to backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Logging
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Checks
Already implemented at `/health` endpoint

---

## Step 7: Security Checklist

- [ ] HTTPS enabled (SSL certificates)
- [ ] Environment variables secured (no hardcoded secrets)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using ORM)
- [ ] API authentication (if needed)
- [ ] Database backups automated

---

## Step 8: Performance Optimization

### Backend
```python
# Add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
```

### Frontend
```typescript
// Next.js config
module.exports = {
  compress: true,
  images: {
    domains: ['your-cdn.com'],
  },
  experimental: {
    optimizeCss: true,
  }
}
```

---

## Step 9: Backup Strategy

### Database Backups
```bash
# Automated daily backups
0 2 * * * pg_dump -h localhost -U postgres lymeric_prod > /backups/lymeric-$(date +\%Y\%m\%d).sql
```

### File Storage
- Store uploaded CSVs/Excel in S3/Cloud Storage
- Keep conversation history backups

---

## Step 10: Post-Deployment Testing

```bash
# Health checks
curl https://api.yourdomain.com/health

# API tests
curl https://api.yourdomain.com/api/materials

# Load testing
ab -n 1000 -c 10 https://api.yourdomain.com/api/materials
```

---

## Estimated Costs

### Render (Starter Plan)
- Backend: $7/month
- Frontend: $7/month
- PostgreSQL: $7/month
- **Total:** ~$21/month

### AWS (Basic Setup)
- EC2 t3.micro: $8/month
- RDS t3.micro: $15/month
- S3 Storage: $1/month
- **Total:** ~$25/month

### GCP (Cloud Run)
- Cloud Run: Pay per use (~$10/month)
- Cloud SQL: $10/month
- **Total:** ~$20/month

---

## Troubleshooting

### Database Connection Issues
```bash
# Check connection
psql $DATABASE_URL -c "SELECT 1"

# View logs
docker logs backend-container
```

### Frontend Not Loading
```bash
# Check build
npm run build

# Check environment
echo $NEXT_PUBLIC_API_URL
```

---

## Support

For deployment issues:
- Check logs: `docker logs <container>`
- Verify environment variables
- Test database connectivity
- Review CORS settings

**Deployment Status:** Ready for production ✅
