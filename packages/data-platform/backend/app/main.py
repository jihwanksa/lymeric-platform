"""FastAPI application entry point for Data Platform"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import materials, datasets, predictions, upload

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lymeric Data Platform API",
    description="Chemistry-aware data platform for materials discovery",
    version="1.0.0"
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
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])

@app.get("/")
def root():
    return {"message": "Lymeric Data Platform API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
