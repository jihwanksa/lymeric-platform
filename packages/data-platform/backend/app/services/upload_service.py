"""Upload service for batch material import from CSV/Excel files"""
import pandas as pd
import io
from typing import Optional, Dict, List, Tuple
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.chemistry_service import ChemistryService
from app.models.material import Material


class UploadService:
    """Service for handling file uploads and batch imports"""
    
    @staticmethod
    async def parse_file(file: UploadFile) -> pd.DataFrame:
        """
        Parse uploaded CSV or Excel file into DataFrame
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            DataFrame with file contents
            
        Raises:
            ValueError: If file format is not supported
        """
        content = await file.read()
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
            return df
        except Exception as e:
            raise ValueError(f"Failed to parse file: {str(e)}")
    
    @staticmethod
    def detect_smiles_column(df: pd.DataFrame) -> Optional[str]:
        """
        Auto-detect which column contains SMILES strings
        
        Strategy:
        1. Check for columns named 'smiles' (case-insensitive)
        2. Check for columns with high percentage of valid SMILES
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Column name containing SMILES, or None if not found
        """
        # Strategy 1: Check column names
        for col in df.columns:
            if 'smiles' in col.lower():
                return col
        
        # Strategy 2: Check content validity
        best_col = None
        best_score = 0
        
        for col in df.columns:
            if df[col].dtype != 'object':  # Skip numeric columns
                continue
            
            # Sample first 10 rows
            sample = df[col].head(10).dropna()
            if len(sample) == 0:
                continue
            
            # Count how many are valid SMILES
            valid_count = sum(
                1 for smiles in sample 
                if ChemistryService.validate_smiles(str(smiles))
            )
            score = valid_count / len(sample)
            
            if score > best_score:
                best_score = score
                best_col = col
        
        # Return if >50% valid SMILES
        return best_col if best_score > 0.5 else None
    
    @staticmethod
    def validate_batch(
        df: pd.DataFrame, 
        smiles_column: str
    ) -> Tuple[List[int], List[Dict]]:
        """
        Validate all SMILES in the specified column
        
        Args:
            df: DataFrame with materials
            smiles_column: Name of column containing SMILES
            
        Returns:
            Tuple of (valid_indices, errors)
            - valid_indices: List of row indices with valid SMILES
            - errors: List of error dicts with row, smiles, error message
        """
        valid_indices = []
        errors = []
        
        for idx, row in df.iterrows():
            smiles = str(row.get(smiles_column, ''))
            
            if pd.isna(row.get(smiles_column)):
                errors.append({
                    'row': int(idx) + 2,  # +2 for 1-indexed + header row
                    'smiles': '',
                    'error': 'Missing SMILES'
                })
                continue
            
            if not ChemistryService.validate_smiles(smiles):
                errors.append({
                    'row': int(idx) + 2,
                    'smiles': smiles,
                    'error': 'Invalid SMILES structure'
                })
                continue
            
            valid_indices.append(idx)
        
        return valid_indices, errors
    
    @staticmethod
    def import_batch(
        df: pd.DataFrame,
        smiles_column: str,
        valid_indices: List[int],
        db: Session,
        skip_duplicates: bool = True
    ) -> Dict:
        """
        Import validated materials with chemistry feature extraction
        
        Args:
            df: DataFrame with materials
            smiles_column: Name of column containing SMILES
            valid_indices: List of row indices to import (pre-validated)
            db: Database session
            skip_duplicates: If True, skip materials with existing canonical SMILES
            
        Returns:
            Dict with import_count, skipped_count, duplicate_count, imported_ids
        """
        imported = []
        skipped = 0
        duplicates = 0
        
        for idx in valid_indices:
            row = df.iloc[idx]
            smiles = str(row[smiles_column])
            
            # Canonicalize SMILES
            canonical_smiles = ChemistryService.canonicalize_smiles(smiles)
            if not canonical_smiles:
                skipped += 1
                continue
            
            # Check for duplicates
            existing = db.query(Material).filter(
                Material.canonical_smiles == canonical_smiles
            ).first()
            
            if existing:
                if skip_duplicates:
                    duplicates += 1
                    continue
                else:
                    skipped += 1
                    continue
            
            # Extract features
            chemistry_features = ChemistryService.extract_all_features(canonical_smiles)
            rdkit_descriptors = ChemistryService.get_rdkit_descriptors(canonical_smiles)
            
            # Get other properties from CSV if present
            material_data = {
                'smiles': smiles,
                'canonical_smiles': canonical_smiles,
                'chemistry_features': chemistry_features,
                'rdkit_descriptors': rdkit_descriptors,
            }
            
            # Try to get name
            if 'name' in row and pd.notna(row['name']):
                material_data['name'] = str(row['name'])
            
            # Try to get property values (lowercase column names)
            for prop in ['tg', 'ffv', 'tc', 'density', 'rg']:
                for col in df.columns:
                    if col.lower() == prop and pd.notna(row[col]):
                        material_data[prop] = float(row[col])
                        break
            
            # Create material
            db_material = Material(**material_data)
            db.add(db_material)
            imported.append(str(db_material.id))
        
        # Commit all at once
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to import materials: {str(e)}")
        
        return {
            'imported_count': len(imported),
            'skipped_count': skipped,
            'duplicate_count': duplicates,
            'imported_ids': imported
        }
