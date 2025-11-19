"""Data quality service for analyzing material completeness and outliers"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
import numpy as np
from app.models.material import Material


class DataQualityService:
    """Service for data quality analysis"""
    
    PROPERTY_COLUMNS = ['tg', 'ffv', 'tc', 'density', 'rg']
    
    @staticmethod
    def get_completeness_analysis(db: Session) -> Dict:
        """
        Analyze completeness of property measurements
        
        Returns:
        {
            'total_materials': int,
            'property_completeness': {
                'tg': {'count': int, 'percentage': float},
                ...
            },
            'completeness_matrix': [  # For heatmap
                {'material_id': str, 'name': str, 'tg': bool, 'ffv': bool, ...}
            ]
        }
        """
        total_materials = db.query(Material).count()
        
        if total_materials == 0:
            return {
                'total_materials': 0,
                'property_completeness': {},
                'completeness_matrix': []
            }
        
        # Count non-null values for each property
        property_completeness = {}
        for prop in DataQualityService.PROPERTY_COLUMNS:
            col = getattr(Material, prop)
            count = db.query(func.count(col)).filter(col.isnot(None)).scalar()
            property_completeness[prop] = {
                'count': count,
                'percentage': round((count / total_materials) * 100, 1)
            }
        
        # Get completeness matrix for heatmap (first 100 materials)
        materials = db.query(Material).limit(100).all()
        completeness_matrix = []
        
        for material in materials:
            row = {
                'material_id': str(material.id),
                'name': material.name or material.smiles[:20],
            }
            for prop in DataQualityService.PROPERTY_COLUMNS:
                row[prop] = getattr(material, prop) is not None
            completeness_matrix.append(row)
        
        return {
            'total_materials': total_materials,
            'property_completeness': property_completeness,
            'completeness_matrix': completeness_matrix
        }
    
    @staticmethod
    def get_outlier_analysis(db: Session) -> Dict:
        """
        Detect outliers using Z-score method (|Z| > 3)
        
        Returns:
        {
            'tg': {
                'outliers': [{'id': str, 'name': str, 'value': float, 'z_score': float}],
                'count': int
            },
            ...
        }
        """
        outliers_by_property = {}
        
        for prop in DataQualityService.PROPERTY_COLUMNS:
            col = getattr(Material, prop)
            
            # Get all non-null values
            materials = db.query(Material).filter(col.isnot(None)).all()
            
            if len(materials) < 3:  # Need at least 3 points for std
                outliers_by_property[prop] = {'outliers': [], 'count': 0}
                continue
            
            values = [getattr(m, prop) for m in materials]
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:  # All values are the same
                outliers_by_property[prop] = {'outliers': [], 'count': 0}
                continue
            
            # Find outliers (|Z| > 3)
            outliers = []
            for material in materials:
                value = getattr(material, prop)
                z_score = (value - mean) / std
                
                if abs(z_score) > 3:
                    outliers.append({
                        'id': str(material.id),
                        'name': material.name or material.smiles[:20],
                        'value': round(value, 3),
                        'z_score': round(z_score, 2)
                    })
            
            outliers_by_property[prop] = {
                'outliers': outliers[:10],  # Limit to 10 outliers
                'count': len(outliers)
            }
        
        return outliers_by_property
    
    @staticmethod
    def get_distribution_stats(db: Session) -> Dict:
        """
        Get distribution statistics for each property
        
        Returns:
        {
            'tg': {
                'mean': float,
                'median': float,
                'std': float,
                'min': float,
                'max': float,
                'q1': float,  # 25th percentile
                'q3': float,  # 75th percentile
                'histogram': [{'bin': str, 'count': int}]
            },
            ...
        }
        """
        distribution_by_property = {}
        
        for prop in DataQualityService.PROPERTY_COLUMNS:
            col = getattr(Material, prop)
            
            # Get all non-null values
            materials = db.query(Material).filter(col.isnot(None)).all()
            
            if len(materials) == 0:
                distribution_by_property[prop] = None
                continue
            
            values = np.array([getattr(m, prop) for m in materials])
            
            # Calculate statistics
            stats = {
                'count': len(values),
                'mean': round(float(np.mean(values)), 3),
                'median': round(float(np.median(values)), 3),
                'std': round(float(np.std(values)), 3),
                'min': round(float(np.min(values)), 3),
                'max': round(float(np.max(values)), 3),
                'q1': round(float(np.percentile(values, 25)), 3),
                'q3': round(float(np.percentile(values, 75)), 3),
            }
            
            # Create histogram (10 bins)
            hist, bin_edges = np.histogram(values, bins=10)
            histogram = []
            for i in range(len(hist)):
                bin_label = f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}"
                histogram.append({
                    'bin': bin_label,
                    'count': int(hist[i]),
                    'range_start': round(float(bin_edges[i]), 3),
                    'range_end': round(float(bin_edges[i+1]), 3)
                })
            
            stats['histogram'] = histogram
            distribution_by_property[prop] = stats
        
        return distribution_by_property
    
    @staticmethod
    def get_quality_summary(db: Session) -> Dict:
        """
        Get complete data quality summary
        
        Combines completeness, outliers, and distribution analysis
        """
        return {
            'completeness': DataQualityService.get_completeness_analysis(db),
            'outliers': DataQualityService.get_outlier_analysis(db),
            'distributions': DataQualityService.get_distribution_stats(db)
        }
