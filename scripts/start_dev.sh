#!/bin/bash
# Quick start script for local development

set -e

echo "🚀 Starting Lymeric Platform..."

# Start databases with Docker
echo "📦 Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

# Wait for postgres to be ready
echo "⏳ Waiting for PostgreSQL..."
sleep 3

# Start backend
echo "🔧 Starting Backend API..."
cd packages/data-platform/backend
source venv/bin/activate

# Run in background
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Start frontend
echo "🎨 Starting Frontend..."
cd ../frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "✅ Platform is running!"
echo ""
echo "Access your application:"
echo "  📊 Frontend:  http://localhost:3000"
echo "  🔌 Backend:   http://localhost:8000/docs"
echo "  🗄️  Database:  localhost:5432"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  docker compose down"
