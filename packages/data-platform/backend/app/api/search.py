"""Search API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.services.search_service import SearchService

router = APIRouter()


class SearchRequest(BaseModel):
    """Search request"""
    query_smiles: str
    threshold: float = 0.7
    limit: int = 100


class SearchResult(BaseModel):
    """Search result item"""
    id: str
    name: str
    smiles: str
    canonical_smiles: str
    similarity: float = None  # For similarity search


@router.post("/substructure", response_model=List[SearchResult])
async def substructure_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Find materials containing the query as a substructure
    
    Uses RDKit SubstructMatch for exact substructure matching
    """
    try:
        materials = SearchService.substructure_search(
            db,
            request.query_smiles,
            limit=request.limit
        )
        
        return [
            SearchResult(
                id=str(m.id),
                name=m.name or "Unnamed",
                smiles=m.smiles,
                canonical_smiles=m.canonical_smiles
            )
            for m in materials
        ]
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/similarity", response_model=List[SearchResult])
async def similarity_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Find similar materials using Morgan fingerprints and Tanimoto similarity
    
    Returns materials sorted by similarity score (highest first)
    """
    try:
        results = SearchService.similarity_search(
            db,
            request.query_smiles,
            threshold=request.threshold,
            limit=request.limit
        )
        
        return [
            SearchResult(
                id=str(m.id),
                name=m.name or "Unnamed",
                smiles=m.smiles,
                canonical_smiles=m.canonical_smiles,
                similarity=round(score, 4)
            )
            for m, score in results
        ]
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
