"""Datasets API endpoints - placeholder for future implementation"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_datasets():
    """List all datasets"""
    return {"message": "Datasets endpoint - coming soon"}

@router.post("/")
def create_dataset():
    """Create a new dataset"""
    return {"message": "Create dataset - coming soon"}
