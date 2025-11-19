#!/bin/bash
# Stop all development services

echo "🛑 Stopping Lymeric Platform..."

# Kill backend and frontend processes
echo "Stopping backend and frontend..."
pkill -f "uvicorn app.main"
pkill -f "next dev"

# Stop Docker services
echo "Stopping Docker services..."
docker compose down

echo "✅ All services stopped"
