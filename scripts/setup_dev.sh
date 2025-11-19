#!/bin/bash
# Development environment setup script for Lymeric Platform

set -e  # Exit on error

echo "🚀 Setting up Lymeric Platform development environment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites checked"

# Setup data-platform backend
echo ""
echo "📦 Setting up Data Platform Backend..."
cd packages/data-platform/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Created virtual environment"
fi
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"
cd ../../..

# Setup research-assistant backend  
echo ""
echo "🤖 Setting up Research Assistant Backend..."
cd packages/research-assistant/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Created virtual environment"
fi
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"
cd ../../..

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "   ✅ Created .env (please update with your settings)"
else
    echo "   ℹ️  .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Update .env with your API keys (especially ANTHROPIC_API_KEY when available)"
echo "   2. Start services: docker-compose up -d"
echo "   3. Run database migrations: cd packages/data-platform/backend && alembic upgrade head"
echo "   4. Access services:"
echo "      - Data Platform API: http://localhost:8000/docs"
echo "      - Research Assistant API: http://localhost:8001/docs"
echo "      - PostgreSQL: localhost:5432"
echo ""
