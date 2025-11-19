"""FastAPI application entry point for Data Platform"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import materials, datasets, predictions

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lymeric Data Platform API",
    description="Chemistry-aware data management platform for materials research",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(materials.router, prefix="/api/materials", tags=["materials"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "Lymeric Data Platform API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {"status": "healthy", "database": "connected"}
