"""Upload API endpoints for batch material import"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import tempfile
import os

from app.core.database import get_db
from app.services.upload_service import UploadService

router = APIRouter()

# In-memory storage for uploaded files (use Redis in production)
_file_storage = {}


class PreviewResponse(BaseModel):
    """Response for file preview"""
    file_id: str
    filename: str
    columns: list[str]
    row_count: int
    preview_data: list[dict]
    suggested_smiles_column: Optional[str]


class ValidateRequest(BaseModel):
    """Request for validation"""
    file_id: str
    smiles_column: str


class ValidationResponse(BaseModel):
    """Response for validation"""
    valid_count: int
    invalid_count: int
    errors: list[dict]


class ImportRequest(BaseModel):
    """Request for import"""
    file_id: str
    smiles_column: str
    skip_duplicates: bool = True


class ImportResponse(BaseModel):
    """Response for import"""
    imported_count: int
    skipped_count: int
    duplicate_count: int
    imported_ids: list[str]


@router.post("/preview", response_model=PreviewResponse)
async def upload_and_preview(file: UploadFile = File(...)):
    """
    Upload CSV/Excel file and return preview
    
    - Parses the file
    - Auto-detects SMILES column
    - Returns first 5 rows for preview
    """
    # Validate file size (max 10MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to start
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 10MB)"
        )
    
    # Parse file
    try:
        df = await UploadService.parse_file(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Generate file ID
    file_id = f"upload_{len(_file_storage)}"
    
    # Store DataFrame temporarily
    _file_storage[file_id] = df
    
    # Auto-detect SMILES column
    suggested_column = UploadService.detect_smiles_column(df)
    
    # Prepare preview (first 5 rows)
    preview_data = df.head(5).fillna('').to_dict('records')
    
    return PreviewResponse(
        file_id=file_id,
        filename=file.filename,
        columns=list(df.columns),
        row_count=len(df),
        preview_data=preview_data,
        suggested_smiles_column=suggested_column
    )


@router.post("/validate", response_model=ValidationResponse)
async def validate_smiles(data: ValidateRequest):
    """
    Validate all SMILES in the selected column
    
    Returns validation results with errors
    """
    # Get stored DataFrame
    if data.file_id not in _file_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found. Please upload again."
        )
    
    df = _file_storage[data.file_id]
    
    # Validate column exists
    if data.smiles_column not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{data.smiles_column}' not found"
        )
    
    # Validate all SMILES
    valid_indices, errors = UploadService.validate_batch(df, data.smiles_column)
    
    return ValidationResponse(
        valid_count=len(valid_indices),
        invalid_count=len(errors),
        errors=errors[:100]  # Limit to first 100 errors
    )


@router.post("/import", response_model=ImportResponse)
async def import_materials(data: ImportRequest, db: Session = Depends(get_db)):
    """
    Import validated materials into database
    
    - Extracts chemistry features
    - Skips duplicates if requested
    - Returns import summary
    """
    # Get stored DataFrame
    if data.file_id not in _file_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found. Please upload again."
        )
    
    df = _file_storage[data.file_id]
    
    # Validate column exists
    if data.smiles_column not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column '{data.smiles_column}' not found"
        )
    
    # Validate first
    valid_indices, errors = UploadService.validate_batch(df, data.smiles_column)
    
    if len(valid_indices) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid materials to import"
        )
    
    # Import
    try:
        result = UploadService.import_batch(
            df, 
            data.smiles_column, 
            valid_indices,
            db,
            data.skip_duplicates
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    # Clean up stored file
    del _file_storage[data.file_id]
    
    return ImportResponse(**result)


@router.delete("/clear/{file_id}")
async def clear_upload(file_id: str):
    """Clear uploaded file from memory"""
    if file_id in _file_storage:
        del _file_storage[file_id]
    return {"message": "File cleared"}
