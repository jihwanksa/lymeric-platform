"""Material model - represents a chemical compound with SMILES"""
from sqlalchemy import Column, String, Float, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Material(Base):
    """Material/Chemical compound in the database"""
    __tablename__ = "materials"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=True)
    smiles = Column(Text, nullable=False, index=True)
    canonical_smiles = Column(Text, nullable=False, index=True, unique=True)
    
    # Chemistry features (auto-calculated)
    chemistry_features = Column(JSON, nullable=True)  # 21 features from v85
    rdkit_descriptors = Column(JSON, nullable=True)   # Additional RDKit descriptors
    
    # Measured properties (if available)
    tg = Column(Float, nullable=True)  # Glass transition temperature
    ffv = Column(Float, nullable=True)  # Free volume fraction
    tc = Column(Float, nullable=True)  # Crystallization temperature
    density = Column(Float, nullable=True)
    rg = Column(Float, nullable=True)  # Radius of gyration
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Material(name='{self.name}', smiles='{self.smiles[:20]}...')>"
