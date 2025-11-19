"""Molecule visualization endpoint"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rdkit import Chem
from rdkit.Chem import Draw
import base64
from io import BytesIO

router = APIRouter()


class MoleculeRequest(BaseModel):
    """Request to visualize molecule"""
    smiles: str
    size: int = 400


class MoleculeResponse(BaseModel):
    """Response with molecule image"""
    image_base64: str
    smiles: str
    canonical_smiles: str
    valid: bool


@router.post("/visualize", response_model=MoleculeResponse)
async def visualize_molecule(request: MoleculeRequest):
    """
    Generate 2D visualization of molecule from SMILES
    
    Returns base64-encoded PNG image
    """
    try:
        # Parse SMILES
        mol = Chem.MolFromSmiles(request.smiles)
        
        if mol is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid SMILES string"
            )
        
        # Get canonical SMILES
        canonical = Chem.MolToSmiles(mol)
        
        # Generate 2D image
        img = Draw.MolToImage(mol, size=(request.size, request.size))
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return MoleculeResponse(
            image_base64=img_str,
            smiles=request.smiles,
            canonical_smiles=canonical,
            valid=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error visualizing molecule: {str(e)}"
        )
