#!/bin/bash

# Local Development Start Script (venv)

set -e

echo "🚀 Starting Lymeric Platform (Local venv Mode)"
echo ""

# Check Python 3.11
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif [ -f "/opt/homebrew/bin/python3.11" ]; then
    PYTHON_CMD="/opt/homebrew/bin/python3.11"
elif [ -f "/usr/local/bin/python3.11" ]; then
    PYTHON_CMD="/usr/local/bin/python3.11"
else
    echo "❌ Python 3.11 not found. Please install it first."
    exit 1
fi

echo "✅ Python 3.11 found: $PYTHON_CMD"

# 1. Start PostgreSQL (Docker)
echo ""
echo "📊 Starting PostgreSQL..."
docker compose up -d postgres
sleep 5

# 2. Start Redis (Docker)
echo ""
echo "🔴 Starting Redis..."
docker compose up -d redis
sleep 3

# 3. Setup backend venv
echo ""
echo "🐍 Setting up backend..."
cd packages/data-platform/backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Virtual environment exists"
    source venv/bin/activate
fi

# 4. Start backend
echo ""
echo "🚀 Starting backend on http://localhost:8000..."
export DATABASE_URL="postgresql://lymeric_user:lymeric_password@localhost:5432/lymeric_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="dev-secret-key-change-in-production"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ../../..

# 5. Start frontend
echo ""
echo "🎨 Starting frontend on http://localhost:3000..."
cd packages/data-platform/frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!

cd ../../..

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose stop postgres redis; echo '✅ Stopped'; exit" INT
wait
