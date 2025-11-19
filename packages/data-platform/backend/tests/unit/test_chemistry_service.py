"""Unit tests for ChemistryService"""
import pytest
from app.services.chemistry_service import ChemistryService

class TestChemistryService:
    """Test chemistry service functionality"""
    
    def test_validate_smiles_valid(self):
        """Test SMILES validation with valid input"""
        assert ChemistryService.validate_smiles("CCO") == True  # Ethanol
        assert ChemistryService.validate_smiles("c1ccccc1") == True  # Benzene
        assert ChemistryService.validate_smiles("CC(C)O") == True  # Isopropanol
    
    def test_validate_smiles_invalid(self):
        """Test SMILES validation with invalid input"""
        assert ChemistryService.validate_smiles("XYZ123") == False  # Definitely invalid
        assert ChemistryService.validate_smiles("") == False
    
    def test_canonicalize_smiles(self):
        """Test SMILES canonicalization"""
        # Different representations of same molecule should canonicalize to same string
        smiles1 = "CC(C)C"  # Isobutane
        smiles2 = "C(C)(C)C"  # Same molecule, different notation
        
        canon1 = ChemistryService.canonicalize_smiles(smiles1)
        canon2 = ChemistryService.canonicalize_smiles(smiles2)
        
        assert canon1 == canon2
        assert canon1 is not None
    
    def test_canonicalize_invalid_smiles(self):
        """Test canonicalization with invalid SMILES"""
        result = ChemistryService.canonicalize_smiles("INVALID")
        assert result is None
    
    def test_extract_simple_features(self):
        """Test simple feature extraction"""
        smiles = "CCO"  # Ethanol
        features = ChemistryService.extract_simple_features(smiles)
        
        assert features['smiles_length'] == 3
        assert features['carbon_count'] == 2
        assert features['oxygen_count'] == 1
        assert features['nitrogen_count'] == 0
    
    def test_extract_chemistry_features(self):
        """Test chemistry feature extraction"""
        smiles = "c1ccccc1"  # Benzene
        features = ChemistryService.extract_chemistry_features(smiles)
        
        assert features is not None
        assert 'aromatic_count' in features
        assert 'num_rings' in features
        assert 'mw_estimate' in features
        assert features['aromatic_count'] == 6  # All 6 carbons are aromatic
        assert features['num_rings'] > 0  # Has at least one ring
    
    def test_extract_all_features(self):
        """Test extraction of all 21 features"""
        smiles = "CC(C)O"  # Isopropanol
        features = ChemistryService.extract_all_features(smiles)
        
        assert features is not None
        # Should have 10 simple + 11 chemistry features
        assert len(features) == 21
        
        # Check some expected features
        assert 'smiles_length' in features
        assert 'carbon_count' in features
        assert 'aromatic_count' in features
        assert 'mw_estimate' in features
    
    def test_extract_features_invalid_smiles(self):
        """Test feature extraction with invalid SMILES"""
        features = ChemistryService.extract_all_features("INVALID")
        assert features is None
    
    def test_get_rdkit_descriptors(self):
        """Test RDKit descriptor calculation"""
        smiles = "CCO"  # Ethanol
        descriptors = ChemistryService.get_rdkit_descriptors(smiles)
        
        assert descriptors is not None
        assert 'MolWt' in descriptors
        assert 'LogP' in descriptors
        assert 'TPSA' in descriptors
        assert descriptors['MolWt'] > 0
        assert descriptors['NumHDonors'] == 1  # OH group
        assert descriptors['NumHAcceptors'] == 1  # Oxygen

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
