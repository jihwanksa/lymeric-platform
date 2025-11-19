"""Substructure search service using RDKit"""
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from sqlalchemy.orm import Session
from typing import List, Tuple
from app.models.material import Material


class SearchService:
    """Chemistry-aware search functionality"""
    
    @staticmethod
    def substructure_search(
        db: Session,
        query_smiles: str,
        limit: int = 100
    ) -> List[Material]:
        """
        Find materials containing the query as a substructure
        
        Uses RDKit SubstructMatch for exact substructure matching
        """
        # Parse query SMILES
        query_mol = Chem.MolFromSmiles(query_smiles)
        if query_mol is None:
            raise ValueError("Invalid query SMILES")
        
        # Get all materials
        all_materials = db.query(Material).all()
        
        matches = []
        for material in all_materials:
            if material.canonical_smiles:
                mol = Chem.MolFromSmiles(material.canonical_smiles)
                if mol and mol.HasSubstructMatch(query_mol):
                    matches.append(material)
                    
                    if len(matches) >= limit:
                        break
        
        return matches
    
    @staticmethod
    def similarity_search(
        db: Session,
        query_smiles: str,
        threshold: float = 0.7,
        limit: int = 100
    ) -> List[Tuple[Material, float]]:
        """
        Find similar materials using Morgan fingerprints and Tanimoto similarity
        
        Returns list of (material, similarity_score) tuples
        """
        # Parse query SMILES
        query_mol = Chem.MolFromSmiles(query_smiles)
        if query_mol is None:
            raise ValueError("Invalid query SMILES")
        
        # Generate query fingerprint
        query_fp = AllChem.GetMorganFingerprintAsBitVect(query_mol, 2, nBits=2048)
        
        # Get all materials and calculate similarities
        all_materials = db.query(Material).all()
        
        similarities = []
        for material in all_materials:
            if material.canonical_smiles:
                mol = Chem.MolFromSmiles(material.canonical_smiles)
                if mol:
                    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
                    similarity = DataStructs.TanimotoSimilarity(query_fp, fp)
                    
                    if similarity >= threshold:
                        similarities.append((material, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
