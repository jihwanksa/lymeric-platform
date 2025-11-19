"""Data quality API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.data_quality_service import DataQualityService

router = APIRouter()


@router.get("/summary")
async def get_quality_summary(db: Session = Depends(get_db)):
    """
    Get comprehensive data quality summary
    
    Returns:
    - Completeness analysis
    - Outlier detection
    - Distribution statistics
    """
    return DataQualityService.get_quality_summary(db)


@router.get("/completeness")
async def get_completeness(db: Session = Depends(get_db)):
    """Get property completeness analysis"""
    return DataQualityService.get_completeness_analysis(db)


@router.get("/outliers")
async def get_outliers(db: Session = Depends(get_db)):
    """Get outlier detection results"""
    return DataQualityService.get_outlier_analysis(db)


@router.get("/distributions")
async def get_distributions(db: Session = Depends(get_db)):
    """Get distribution statistics for all properties"""
    return DataQualityService.get_distribution_stats(db)
