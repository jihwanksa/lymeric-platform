"""Materials API endpoints - CRUD operations for materials"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.material import Material
from app.services.chemistry_service import ChemistryService

router = APIRouter()

# Pydantic schemas
class MaterialCreate(BaseModel):
    """Schema for creating a material"""
    name: Optional[str] = None
    smiles: str = Field(..., description="SMILES representation of the molecule")
    tg: Optional[float] = None
    ffv: Optional[float] = None
    tc: Optional[float] = None
    density: Optional[float] = None
    rg: Optional[float] = None

class MaterialResponse(BaseModel):
    """Schema for material response"""
    id: str
    name: Optional[str]
    smiles: str
    canonical_smiles: str
    chemistry_features: Optional[dict]
    rdkit_descriptors: Optional[dict]
    tg: Optional[float]
    ffv: Optional[float]
    tc: Optional[float]
    density: Optional[float]
    rg: Optional[float]
    created_at: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
def create_material(material: MaterialCreate, db: Session = Depends(get_db)):
    """Create a new material with automatic SMILES canonicalization and feature extraction"""
    
    # Validate SMILES
    if not ChemistryService.validate_smiles(material.smiles):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid SMILES: {material.smiles}"
        )
    
    # Canonicalize SMILES
    canonical_smiles = ChemistryService.canonicalize_smiles(material.smiles)
    if not canonical_smiles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to canonicalize SMILES"
        )
    
    # Check if material already exists (by canonical SMILES)
    existing = db.query(Material).filter(Material.canonical_smiles == canonical_smiles).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Material with this SMILES already exists (ID: {existing.id})"
        )
    
    # Extract chemistry features
    chemistry_features = ChemistryService.extract_all_features(canonical_smiles)
    rdkit_descriptors = ChemistryService.get_rdkit_descriptors(canonical_smiles)
    
    # Create material
    db_material = Material(
        name=material.name,
        smiles=material.smiles,
        canonical_smiles=canonical_smiles,
        chemistry_features=chemistry_features,
        rdkit_descriptors=rdkit_descriptors,
        tg=material.tg,
        ffv=material.ffv,
        tc=material.tc,
        density=material.density,
        rg=material.rg
    )
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    return db_material

@router.get("/", response_model=List[MaterialResponse])
def list_materials(
    skip: int = 0,
    limit: int = 100,
    tg_min: Optional[float] = None,
    tg_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """List materials with optional filtering"""
    query = db.query(Material)
    
    # Apply filters
    if tg_min is not None:
        query = query.filter(Material.tg >= tg_min)
    if tg_max is not None:
        query = query.filter(Material.tg <= tg_max)
    
    materials = query.offset(skip).limit(limit).all()
    return materials

@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: str, db: Session = Depends(get_db)):
    """Get a specific material by ID"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material not found: {material_id}"
        )
    return material

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(material_id: str, db: Session = Depends(get_db)):
    """Delete a material"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material not found: {material_id}"
        )
    
    db.delete(material)
    db.commit()
    return None
