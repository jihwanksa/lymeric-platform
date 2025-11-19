"""Export API endpoints for CSV and Excel"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
from io import BytesIO, StringIO
from app.core.database import get_db
from app.models.material import Material

router = APIRouter()


@router.get("/csv")
async def export_csv(
    tg_min: Optional[float] = None,
    tg_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Export materials to CSV file
    
    Supports same filtering as materials list endpoint
    """
    query = db.query(Material)
    
    # Apply filters (same as materials endpoint)
    if tg_min is not None:
        query = query.filter(Material.tg >= tg_min)
    if tg_max is not None:
        query = query.filter(Material.tg <= tg_max)
    
    materials = query.all()
    
    # Convert to DataFrame
    data = []
    for m in materials:
        data.append({
            'id': str(m.id),
            'name': m.name,
            'smiles': m.smiles,
            'canonical_smiles': m.canonical_smiles,
            'tg': m.tg,
            'ffv': m.ffv,
            'tc': m.tc,
            'density': m.density,
            'rg': m.rg,
            'created_at': m.created_at.isoformat() if m.created_at else None
        })
    
    df = pd.DataFrame(data)
    
    # Convert to CSV
    stream = StringIO()
    df.to_csv(stream, index=False)
    
    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=materials_export.csv"
        }
    )


@router.get("/excel")
async def export_excel(
    tg_min: Optional[float] = None,
    tg_max: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Export materials to Excel file with formatting
    """
    query = db.query(Material)
    
    # Apply filters
    if tg_min is not None:
        query = query.filter(Material.tg >= tg_min)
    if tg_max is not None:
        query = query.filter(Material.tg <= tg_max)
    
    materials = query.all()
    
    # Convert to DataFrame
    data = []
    for m in materials:
        data.append({
            'ID': str(m.id),
            'Name': m.name,
            'SMILES': m.smiles,
            'Canonical SMILES': m.canonical_smiles,
            'Tg (°C)': m.tg,
            'FFV': m.ffv,
            'Tc': m.tc,
            'Density (g/cm³)': m.density,
            'Rg (Å)': m.rg,
            'Created': m.created_at.isoformat() if m.created_at else None
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Materials', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Materials']
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=materials_export.xlsx"
        }
    )
