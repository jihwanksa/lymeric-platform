"""Analytics service for property correlations and advanced visualizations"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats
from app.models.material import Material


class AnalyticsService:
    """Service for advanced analytics and visualizations"""
    
    PROPERTY_COLUMNS = ['tg', 'ffv', 'tc', 'density', 'rg']
    
    @staticmethod
    def calculate_correlation(
        x_values: List[float], 
        y_values: List[float]
    ) -> Tuple[float, float]:
        """
        Calculate Pearson correlation coefficient and p-value
        
        Returns:
            (correlation, p_value)
        """
        if len(x_values) < 3:
            return 0.0, 1.0
        
        correlation, p_value = stats.pearsonr(x_values, y_values)
        return float(correlation), float(p_value)
    
    @staticmethod
    def get_correlation_matrix(db: Session) -> Dict:
        """
        Calculate correlation matrix for all property pairs
        
        Returns:
        {
            'matrix': [
                {'x': 'tg', 'y': 'ffv', 'correlation': float, 'p_value': float, 'n': int}
            ],
            'properties': ['tg', 'ffv', 'tc', 'density', 'rg']
        }
        """
        correlations = []
        
        for i, prop_x in enumerate(AnalyticsService.PROPERTY_COLUMNS):
            for j, prop_y in enumerate(AnalyticsService.PROPERTY_COLUMNS):
                if i >= j:  # Skip duplicate pairs and self-correlations
                    continue
                
                # Get materials with both properties
                col_x = getattr(Material, prop_x)
                col_y = getattr(Material, prop_y)
                
                materials = db.query(Material).filter(
                    col_x.isnot(None),
                    col_y.isnot(None)
                ).all()
                
                if len(materials) < 3:
                    continue
                
                x_values = [getattr(m, prop_x) for m in materials]
                y_values = [getattr(m, prop_y) for m in materials]
                
                correlation, p_value = AnalyticsService.calculate_correlation(x_values, y_values)
                
                correlations.append({
                    'x': prop_x,
                    'y': prop_y,
                    'correlation': round(correlation, 3),
                    'p_value': round(p_value, 4),
                    'n': len(materials),
                    'significant': p_value < 0.05
                })
        
        return {
            'matrix': correlations,
            'properties': AnalyticsService.PROPERTY_COLUMNS
        }
    
    @staticmethod
    def get_scatter_data(
        db: Session,
        x_property: str,
        y_property: str,
        limit: int = 500
    ) -> Dict:
        """
        Get scatter plot data for two properties
        
        Returns:
        {
            'data': [{'x': float, 'y': float, 'name': str, 'id': str}],
            'x_property': str,
            'y_property': str,
            'correlation': float,
            'p_value': float,
            'n': int
        }
        """
        if x_property not in AnalyticsService.PROPERTY_COLUMNS:
            raise ValueError(f"Invalid property: {x_property}")
        if y_property not in AnalyticsService.PROPERTY_COLUMNS:
            raise ValueError(f"Invalid property: {y_property}")
        
        # Get materials with both properties
        col_x = getattr(Material, x_property)
        col_y = getattr(Material, y_property)
        
        materials = db.query(Material).filter(
            col_x.isnot(None),
            col_y.isnot(None)
        ).limit(limit).all()
        
        if len(materials) == 0:
            return {
                'data': [],
                'x_property': x_property,
                'y_property': y_property,
                'correlation': 0.0,
                'p_value': 1.0,
                'n': 0
            }
        
        # Prepare scatter data
        scatter_data = []
        x_values = []
        y_values = []
        
        for material in materials:
            x_val = getattr(material, x_property)
            y_val = getattr(material, y_property)
            
            scatter_data.append({
                'x': round(x_val, 3),
                'y': round(y_val, 3),
                'name': material.name or material.smiles[:20],
                'id': str(material.id)
            })
            
            x_values.append(x_val)
            y_values.append(y_val)
        
        # Calculate correlation
        correlation, p_value = AnalyticsService.calculate_correlation(x_values, y_values)
        
        return {
            'data': scatter_data,
            'x_property': x_property,
            'y_property': y_property,
            'correlation': round(correlation, 3),
            'p_value': round(p_value, 4),
            'n': len(materials)
        }
    
    @staticmethod
    def get_property_comparison(
        db: Session,
        properties: List[str] = None
    ) -> Dict:
        """
        Get comparison data for multiple properties
        
        Useful for parallel coordinate plots or radar charts
        """
        if properties is None:
            properties = AnalyticsService.PROPERTY_COLUMNS
        
        # Validate properties
        for prop in properties:
            if prop not in AnalyticsService.PROPERTY_COLUMNS:
                raise ValueError(f"Invalid property: {prop}")
        
        # Get materials with all specified properties
        query = db.query(Material)
        for prop in properties:
            col = getattr(Material, prop)
            query = query.filter(col.isnot(None))
        
        materials = query.limit(100).all()
        
        comparison_data = []
        for material in materials:
            data_point = {
                'name': material.name or material.smiles[:20],
                'id': str(material.id)
            }
            for prop in properties:
                data_point[prop] = round(getattr(material, prop), 3)
            comparison_data.append(data_point)
        
        return {
            'data': comparison_data,
            'properties': properties,
            'n': len(materials)
        }
