# Quick Start Guide - Lymeric Platform

Get up and running in **5 minutes** with zero configuration hassles.

## ✅ Prerequisites Check

Before starting, verify you have:

```bash
# Check Docker is installed and running
docker --version
# Should show: Docker version 20.x or higher

# Check Docker Compose
docker compose version
# Should show: Docker Compose version v2.x or higher

# Check available disk space
df -h .
# Need at least 10GB free
```

## 🚀 Start Everything

```bash
# 1. Start database and cache
docker compose up -d postgres redis

# 2. Wait for them to be healthy (15 seconds)
sleep 15

# 3. Start backend
docker compose up -d data-platform-backend

# 4. Verify backend is running
curl http://localhost:8000/
# Should return: {"message":"Lymeric Data Platform API"}

# 5. Start frontend (in new terminal)
cd packages/data-platform/frontend
npm install  # Only needed first time
npm run dev
```

## 🐍 Option 2: Local Development (Hybrid)

Use this if you want to run Python/Node locally but keep databases in Docker. Best for development!

```bash
# 1. Run the helper script
./scripts/start_local.sh
```

This script automatically:
- Starts PostgreSQL & Redis (in Docker)
- Creates a Python 3.11 virtual environment
- Installs all dependencies
- Starts Backend (port 8000) & Frontend (port 3000)

**Prerequisites:**
- Python 3.11 installed
- Node.js 18+ installed
- Docker Desktop running (for databases)

**Done!** Open http://localhost:3000

## 🧪 Verify It Works

### Test 1: Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test12Test34"}'
```

**Success looks like:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "email": "test@example.com"
}
```

### Test 2: Search (Returns Empty - That's OK!)

```bash
curl -X POST http://localhost:8000/api/search/substructure \
  -H "Content-Type: application/json" \
  -d '{"query_smiles":"c1ccccc1","limit":10}'
```

**Success looks like:**
```json
[]
```
_(Empty because no data yet - that's expected!)_

## 🎨 Use the Web Interface

1. **Register:** http://localhost:3000/register
2. **Login:** http://localhost:3000/login
3. **Search:** http://localhost:3000/search
4. **Train ML Model:** http://localhost:3000/training
5. **Upload Data:** http://localhost:3000/upload

## 🛑 Stop Everything

```bash
# Stop all services
docker compose down

# Stop and remove all data (fresh start)
docker compose down -v
```

## ❌ Common Issues & Fixes

### "Port 8000 already in use"

```bash
# Find what's using the port
lsof -ti:8000

# Kill it
lsof -ti:8000 | xargs kill -9

# Restart backend
docker compose up -d data-platform-backend
```

### "Failed to fetch" in browser

```bash
# 1. Check backend is running
curl http://localhost:8000/

# 2. Check backend logs for errors
docker logs lymeric-data-backend --tail 50

# 3. Restart if needed
docker compose restart data-platform-backend
```

### Backend crashes on startup

```bash
# View full error
docker logs lymeric-data-backend

# Common fix: Rebuild with --no-cache
docker compose build --no-cache data-platform-backend
docker compose up -d data-platform-backend
```

### Database connection failed

```bash
# Reset database
docker compose down -v
docker compose up -d postgres redis
sleep 15
docker compose up -d data-platform-backend
```

## 📊 Check Service Health

```bash
# See all running containers
docker ps

# Should show:
# - lymeric-postgres (healthy)
# - lymeric-redis (healthy)
# - lymeric-data-backend (up)

# Check backend logs
docker logs lymeric-data-backend --tail 20 -f

# Check database logs
docker logs lymeric-postgres --tail 20
```

## 🎯 Next Steps

1. **Upload sample data:** Use http://localhost:3000/upload
2. **Train a model:** Visit http://localhost:3000/training
3. **Explore visualizations:** Check http://localhost:3000/visualizations

## 🆘 Still Having Issues?

1. **Check Docker has enough resources:**
   - Docker Desktop → Settings → Resources
   - Minimum: 4 CPUs, 8GB RAM

2. **View detailed logs:**
   ```bash
   docker logs lymeric-data-backend 2>&1 | tail -100
   ```

3. **Nuclear option (fresh start):**
   ```bash
   docker compose down -v
   docker system prune -a
   # Then start from step 1
   ```

---

**Estimated time: 5 minutes** ⏱️

**Works on:** macOS, Linux, Windows (WSL2) 🖥️
