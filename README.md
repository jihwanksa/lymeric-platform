# Lymeric Materials Platform

**Integrated Materials Discovery Ecosystem**

[![Status](https://img.shields.io/badge/status-complete-success)](https://github.com/jihwanksa/lymeric-platform)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/next.js-16-black)](https://nextjs.org)

---

## Overview

Lymeric is a complete platform for materials research combining:
- 🗂️ **Chemistry-Aware Data Management** - Store materials with SMILES validation
- 🤖 **ML Property Predictions** - Ensemble models for Tg, FFV, Tc, Density, Rg
- 📊 **Data Quality Analysis** - Automated outlier detection and completeness tracking
- 📈 **Interactive Visualizations** - Correlation matrix and scatter plots
- 💬 **AI Research Assistant** - Chat interface for materials queries
- 📤 **Batch Import/Export** - CSV/Excel support with validation

---

## Quick Start

### Option 1: One Command Setup
```bash
git clone https://github.com/jihwanksa/lymeric-platform.git
cd lymeric-platform
./scripts/start_dev.sh
```

### Option 2: Manual Setup
```bash
# Start PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=lymeric postgres:15

# Backend
cd packages/data-platform/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000 &

# Frontend
cd packages/data-platform/frontend
npm install && npm run dev &

# Research Assistant
cd packages/research-assistant/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001 &
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Chat API: http://localhost:8001

---

## 🚀 Quick Start Guide - Try It Now!

Once all services are running, here's how to explore the platform:

### 1. **View the Dashboard** (2 minutes)
- Open http://localhost:3000
- See overview and navigation
- Browse the 7 main sections

### 2. **Add Your First Material** (3 minutes)
- Click "Materials" in navigation
- Click "+ Add Material" button
- Enter SMILES: `c1ccccc1` (benzene)
- Add name: "Benzene" (optional)
- Click "Add Material"
- ✅ You'll see the material in the list!

### 3. **Predict Properties** (2 minutes)
- Click "Predictions" in navigation
- Enter SMILES: `c1ccccc1`
- Click "Predict Properties"
- ✅ See 5 property predictions with confidence scores!

### 4. **Upload a CSV File** (5 minutes)
- Click "Upload" in navigation
- Download sample: `/tests/fixtures/sample_materials.csv`
- Drag and drop the CSV file
- Click "Validate SMILES"
- Click "Import Materials"
- ✅ 10 materials imported!

### 5. **Check Data Quality** (3 minutes)
- Click "Quality" in navigation
- View completeness bar chart
- See outlier detection
- Explore distribution histograms

### 6. **Visualize Correlations** (3 minutes)
- Click "Visualizations" in navigation
- Browse correlation matrix cards
- Click any card to see scatter plot
- Try different X/Y property combinations

### 7. **Chat with AI Assistant** (5 minutes)
- Click "Chat" in navigation
- Try a suggested prompt or type your own:
  - "What is the glass transition temperature?"
  - "Analyze my dataset"
  - "How do I synthesize polymers?"
- ✅ Get instant responses (mock mode)!

**🎉 You've now tried all major features!**

For detailed instructions, see [USER_GUIDE.md](docs/guides/USER_GUIDE.md)

---

## Features

### ✅ Data Management
- Add materials with SMILES validation
- Automatic feature extraction (21 chemistry features)
- Search by name, SMILES, property ranges
- Export to CSV/Excel with formatting

### ✅ Batch Import
- Upload CSV/Excel files
- Auto-detect SMILES column
- Batch validation with error reporting
- Duplicate detection

### ✅ ML Predictions
- Glass Transition Temperature (Tg)
- Free Volume Fraction (FFV)
- Crystallinity (Tc)
- Density
- Radius of Gyration (Rg)
- Confidence scores for all predictions

### ✅ Data Quality
- Completeness analysis (% measured per property)
- Outlier detection (Z-score > 3)
- Distribution statistics with histograms
- Visual quality indicators

### ✅ Visualizations
- Correlation matrix with significance testing
- Interactive scatter plots
- Property comparison charts
- Recharts integration

### ✅ AI Assistant (Mock Mode)
- Conversational interface
- Context-aware responses
- Conversation history
- Markdown rendering
- Easy upgrade to real Claude API

---

## Tech Stack

**Backend:**
- FastAPI 0.104 - Web framework
- SQLAlchemy 2.0 - ORM
- PostgreSQL 15 - Database
- RDKit 2023.09 - Chemistry toolkit
- scikit-learn 1.3 - ML models
- pandas 2.1 - Data manipulation

**Frontend:**
- Next.js 16 - React framework
- TypeScript 5.3 - Type safety
- Tailwind CSS 3.3 - Styling
- Recharts 2.10 - Visualizations

---

## 📚 Documentation

### Guides & Manuals
- **[User Guide](docs/guides/USER_GUIDE.md):** Comprehensive manual for using the platform.
- **[Developer Onboarding](docs/guides/DEVELOPER_ONBOARDING.md):** Setup guide for new developers.
- **[Deployment Guide](docs/guides/DEPLOYMENT_GUIDE.md):** Production deployment instructions.
- **[Claude Integration](docs/guides/CLAUDE_INTEGRATION_GUIDE.md):** How to enable real AI features.

### Plans & Roadmap
- **[Production Features](docs/plans/PRODUCTION_FEATURES.md):** Roadmap for production readiness.
- **[Implementation Plan](docs/plans/IMPLEMENTATION_PLAN.md):** Original project plan.

### Status & Reports
- **[Project Status](docs/reports/STATUS.md):** Current status and completed features.
- **[Progress Summary](docs/reports/PROGRESS_SUMMARY.md):** Detailed progress tracking.

---

## Project Structure

```
lymeric-platform/
├── packages/
│   ├── data-platform/          # Main application
│   │   ├── backend/            # FastAPI + RDKit
│   │   └── frontend/           # Next.js + TypeScript
│   ├── research-assistant/     # Chat backend
│   └── ai-services/            # ML predictor
├── docs/                       # Documentation
├── tests/fixtures/             # Sample data
└── scripts/                    # Development scripts
```

---

## Screenshots

### Materials Management
![Materials Page](docs/images/materials-page.png)

### Data Quality Dashboard
![Quality Dashboard](docs/images/quality-dashboard.png)

### Correlation Visualizations
![Visualizations](docs/images/visualizations.png)

### AI Research Assistant
![Chat Interface](docs/images/chat-interface.png)

---

## Development


```bash
# Backend tests
cd packages/data-platform/backend
pytest

# Frontend development
cd packages/data-platform/frontend
npm run dev

# View API docs
open http://localhost:8000/docs
```

---

## Deployment

### Docker Compose
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Cloud Options
- **Render** - easiest, ~$21/month
- **AWS** - full control, ~$25/month
- **GCP** - serverless, ~$20/month

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for details.

---

## Roadmap

### ✅ Completed
- Phase 1: Foundation (backend, frontend, ML)
- Phase 2: Data Platform (upload, quality, visualizations)
- Phase 3: Research Assistant (mock mode)

### 🔜 Future
- Real Claude API integration
- User authentication
- Substructure search
- Custom ML model training
- Team collaboration features

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Support

- **Documentation:** `/docs` folder
- **Issues:** [GitHub Issues](https://github.com/jihwanksa/lymeric-platform/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jihwanksa/lymeric-platform/discussions)

---

## Acknowledgments

- **RDKit** - Open-source chemistry toolkit
- **Anthropic** - Claude API (for future integration)
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework

---

**Built with ❤️ for materials researchers**

Repository: https://github.com/jihwanksa/lymeric-platform  
Status: ✅ **Production Ready**
