# Lymeric Materials Platform

**An integrated materials discovery ecosystem for chemistry research and AI-powered analysis.**

## Overview

The Lymeric Materials Platform consists of three interconnected components:

1. **Data Platform** - Chemistry-aware data management for polymer research
2. **Research Assistant** - AI chatbot enhanced with domain expertise via Claude Skills
3. **AI Services** - Machine learning models for property prediction (from open_polymer proof of concept)

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

### Development Setup

```bash
# Run setup script
./scripts/setup_dev.sh

# Start all services
docker-compose up -d

# Access services
# Data Platform Frontend: http://localhost:3000
# Research Assistant: http://localhost:3001
# API Documentation: http://localhost:8000/docs
```

## Documentation

See `docs/` for detailed documentation.

## License

MIT License
