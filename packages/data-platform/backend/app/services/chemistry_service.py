"""Chemistry service using RDKit for SMILES processing and feature extraction"""
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem
from typing import Optional, Dict
import re

class ChemistryService:
    """Chemistry operations using RDKit"""
    
    @staticmethod
    def canonicalize_smiles(smiles: str) -> Optional[str]:
        """Convert SMILES to canonical form"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            return Chem.MolToSmiles(mol, canonical=True)
        except Exception:
            return None
    
    @staticmethod
    def validate_smiles(smiles: str) -> bool:
        """Check if SMILES is valid"""
        if not smiles:  # Reject empty strings
            return False
        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except Exception:
            return False
    
    @staticmethod
    def extract_simple_features(smiles: str) -> Dict:
        """Extract 10 simple features from SMILES (like v85 baseline)"""
        features = {
            'smiles_length': len(smiles),
            'carbon_count': smiles.count('C'),
            'nitrogen_count': smiles.count('N'),
            'oxygen_count': smiles.count('O'),
            'sulfur_count': smiles.count('S'),
            'fluorine_count': smiles.count('F'),
            'ring_count': smiles.count('1') + smiles.count('2'),
            'double_bond_count': smiles.count('='),
            'triple_bond_count': smiles.count('#'),
            'branch_count': smiles.count('(')
        }
        return features
    
    @staticmethod
    def extract_chemistry_features(smiles: str) -> Optional[Dict]:
        """Extract 11 chemistry-based features (like v85 enhancement)"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            
            # Count bonds by type
            single_bonds = sum(1 for bond in mol.GetBonds() if bond.GetBondType() == Chem.BondType.SINGLE)
            aromatic_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
            
            # H-bond donors and acceptors
            h_bond_donors = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() in ['O', 'N'] and atom.GetTotalNumHs() > 0)
            h_bond_acceptors = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() in ['O', 'N'])
            
            # Ring count as integer
            num_rings = len(Chem.GetSSSR(mol))  # Get length of ring set
            
            # Halogen and heteroatom counts
            halogen_count = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() in ['F', 'Cl', 'Br', 'I'])
            heteroatom_count = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() in ['N', 'O', 'S'])
            
            # Molecular weight estimate
            mw_estimate = Descriptors.MolWt(mol)
            
            # Backbone and branching (simplified)
            num_carbons = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() == 'C')
            num_side_chains = sum(1 for atom in mol.GetAtoms() if atom.GetDegree() > 2)
            backbone_carbons = num_carbons - num_side_chains
            branching_ratio = num_side_chains / max(backbone_carbons, 1)
            
            features = {
                'num_side_chains': num_side_chains,
                'backbone_carbons': backbone_carbons,
                'branching_ratio': branching_ratio,
                'aromatic_count': aromatic_atoms,
                'h_bond_donors': h_bond_donors,
                'h_bond_acceptors': h_bond_acceptors,
                'num_rings': num_rings,
                'single_bonds': single_bonds,
                'halogen_count': halogen_count,
                'heteroatom_count': heteroatom_count,
                'mw_estimate': mw_estimate
            }
            return features
        except Exception:
            return None
    
    @staticmethod
    def extract_all_features(smiles: str) -> Optional[Dict]:
        """Extract all 21 features (10 simple + 11 chemistry)"""
        simple = ChemistryService.extract_simple_features(smiles)
        chemistry = ChemistryService.extract_chemistry_features(smiles)
        
        if chemistry is None:
            return None
        
        return {**simple, **chemistry}
    
    @staticmethod
    def get_rdkit_descriptors(smiles: str) -> Optional[Dict]:
        """Get additional RDKit molecular descriptors"""
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            
            descriptors = {
                'MolWt': Descriptors.MolWt(mol),
                'LogP': Descriptors.MolLogP(mol),
                'TPSA': Descriptors.TPSA(mol),
                'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
                'NumHAcceptors': Descriptors.NumHAcceptors(mol),
                'NumHDonors': Descriptors.NumHDonors(mol),
                'NumAromaticRings': Descriptors.NumAromaticRings(mol),
                'NumAliphaticRings': Descriptors.NumAliphaticRings(mol)
            }
            return descriptors
        except Exception:
            return None
