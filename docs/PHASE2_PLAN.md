# Phase 2 Implementation Plan: CSV Upload & Data Quality

## Priority 1: CSV Upload Feature

### Goal
Enable users to upload CSV/Excel files containing multiple materials with SMILES, automatically validate them, extract chemistry features, and import them in batch.

### User Flow
1. User navigates to `/upload` page
2. Drags and drops a CSV file (or clicks to browse)
3. System parses CSV and shows preview table
4. User selects which column contains SMILES
5. System validates all SMILES (shows errors if any)
6. User clicks "Import" button
7. System imports all valid materials with auto-feature extraction
8. Shows import summary (X succeeded, Y failed, Z duplicates)

---

## Backend Implementation

### 1. File Upload Service
**File:** `packages/data-platform/backend/app/services/upload_service.py`

```python
class UploadService:
    @staticmethod
    def parse_csv(file) -> pd.DataFrame:
        """Parse CSV file into DataFrame"""
        
    @staticmethod
    def detect_smiles_column(df: pd.DataFrame) -> str:
        """Auto-detect which column contains SMILES"""
        
    @staticmethod
    def validate_batch(df: pd.DataFrame, smiles_col: str) -> dict:
        """Validate all SMILES, return errors"""
        
    @staticmethod
    def import_batch(df: pd.DataFrame, smiles_col: str, db: Session) -> dict:
        """Import all materials with feature extraction"""
```

### 2. Upload API Endpoints
**File:** `packages/data-platform/backend/app/api/upload.py`

**Endpoint 1: Upload & Preview**
```python
@router.post("/preview")
async def upload_preview(file: UploadFile):
    """
    Upload CSV, parse, and return preview
    
    Returns:
    {
        "filename": "materials.csv",
        "columns": ["name", "smiles", "tg", "density"],
        "rows": 10,
        "preview": [{...}],  # First 5 rows
        "suggested_smiles_column": "smiles"
    }
    """
```

**Endpoint 2: Validate**
```python
@router.post("/validate")
async def validate_upload(data: ValidateRequest):
    """
    Validate all SMILES in selected column
    
    Request:
    {
        "file_id": "temp_id",
        "smiles_column": "smiles"
    }
    
    Returns:
    {
        "valid_count": 95,
        "invalid_count": 5,
        "errors": [
            {"row": 3, "smiles": "invalid", "error": "..."},
            ...
        ]
    }
    """
```

**Endpoint 3: Import**
```python
@router.post("/import")
async def import_materials(data: ImportRequest, db: Session):
    """
    Import all valid materials
    
    Request:
    {
        "file_id": "temp_id",
        "smiles_column": "smiles",
        "skip_duplicates": true
    }
    
    Returns:
    {
        "imported": 95,
        "skipped": 5,
        "errors": 0,
        "materials": [...]  # IDs of imported materials
    }
    """
```

---

## Frontend Implementation

### 1. Upload Page
**File:** `packages/data-platform/frontend/app/upload/page.tsx`

**Features:**
- Drag-and-drop zone (react-dropzone)
- File preview table
- Column selector dropdown
- Validation results display
- Import button with progress
- Success/error summary

**State Management:**
```typescript
const [file, setFile] = useState<File | null>(null);
const [preview, setPreview] = useState<PreviewData | null>(null);
const [smilesColumn, setSmilesColumn] = useState<string>("");
const [validationResults, setValidationResults] = useState(null);
const [importing, setImporting] = useState(false);
```

---

## Dependencies

### Backend
```bash
pip install pandas openpyxl  # Excel support
```

### Frontend
```bash
npm install react-dropzone recharts
```

---

## Testing Plan

### Backend Tests
1. **CSV Parsing:**
   - Test with valid CSV
   - Test with Excel file
   - Test with invalid format
   
2. **SMILES Detection:**
   - Column named "SMILES" (case-insensitive)
   - Column with most valid SMILES strings
   
3. **Batch Validation:**
   - 100 valid SMILES → all pass
   - Mix of valid/invalid → correct error reporting
   
4. **Batch Import:**
   - Extract features for all materials
   - Handle duplicates correctly
   - Return accurate summary

### Frontend Tests
1. File upload works
2. Preview displays correctly
3. Column selector updates validation
4. Import shows progress
5. Success message displays summary

---

## Acceptance Criteria

✅ User can upload CSV/Excel file  
✅ System auto-detects SMILES column  
✅ All SMILES are validated before import  
✅ Invalid SMILES are reported with row numbers  
✅ Valid materials are imported with chemistry features  
✅ Duplicates are detected and skipped  
✅ Import summary shows counts (imported/skipped/errors)  
✅ Materials page reflects newly imported materials  

---

## Estimated Timeline

- **Day 1:** Backend upload service + CSV parsing (4 hours)
- **Day 2:** Backend validation & import logic (4 hours)
- **Day 3:** Frontend upload page UI (4 hours)
- **Day 4:** Integration testing & refinement (4 hours)

**Total:** 4 days

---

## Next: Data Quality Dashboard

After CSV upload is complete, we'll implement:
- Completeness heatmap
- Outlier detection
- Property distributions
