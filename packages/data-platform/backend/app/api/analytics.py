"""Analytics API endpoints for correlations and visualizations"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/correlations")
async def get_correlations(db: Session = Depends(get_db)):
    """
    Get correlation matrix for all property pairs
    
    Returns Pearson correlation coefficients with p-values
    """
    return AnalyticsService.get_correlation_matrix(db)


@router.get("/scatter")
async def get_scatter_plot(
    x: str = Query(..., description="X-axis property"),
    y: str = Query(..., description="Y-axis property"),
    limit: int = Query(500, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get scatter plot data for two properties
    
    Returns data points with correlation statistics
    """
    try:
        return AnalyticsService.get_scatter_data(db, x, y, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/comparison")
async def get_property_comparison(
    properties: Optional[str] = Query(None, description="Comma-separated property names"),
    db: Session = Depends(get_db)
):
    """
    Get comparison data for multiple properties
    
    Useful for parallel coordinates or radar charts
    """
    if properties:
        prop_list = [p.strip() for p in properties.split(',')]
    else:
        prop_list = None
    
    try:
        return AnalyticsService.get_property_comparison(db, prop_list)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
