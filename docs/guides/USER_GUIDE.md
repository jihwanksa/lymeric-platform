# Lymeric Platform - User Guide

**Getting Started with Materials Research Platform**

---

## What is Lymeric Platform?

Lymeric is an integrated materials discovery platform that helps you:
- **Store** material data with chemistry validation
- **Predict** properties using machine learning
- **Analyze** data quality automatically
- **Visualize** relationships between properties
- **Chat** with an AI research assistant

---

## Quick Start

### Accessing the Platform

1. Open your browser to http://localhost:3000
2. You'll see the navigation bar with 7 sections

### Navigation

- **Dashboard** - Overview and statistics
- **Materials** - Browse and add materials
- **Upload** - Batch import from CSV/Excel
- **Quality** - Data quality analysis
- **Visualizations** - Property correlations
- **Chat** - AI research assistant
- **Predictions** - ML property predictions

---

## Features Guide

### 1. Adding Materials

**Single Material:**
1. Click "Materials" in navigation
2. Click "+ Add Material"
3. Enter SMILES notation (e.g., `c1ccccc1` for benzene)
4. Optionally add a name
5. Click "Add Material"

**Example SMILES:**
- Benzene: `c1ccccc1`
- Toluene: `Cc1ccccc1`
- Styrene: `C=Cc1ccccc1`

**What Happens:**
- SMILES is validated
- Canonical form is generated
- 21 chemistry features are extracted automatically

---

### 2. Batch Upload (CSV/Excel)

**Prepare Your File:**

Create a CSV or Excel file with at least a SMILES column:

```csv
name,smiles,tg,density
Benzene,c1ccccc1,551.06,0.994
Toluene,Cc1ccccc1,535.23,0.867
```

**Upload Process:**

1. Click "Upload" in navigation
2. Click "Choose File" and select your CSV/Excel
3. System auto-detects SMILES column ✨
4. Review preview (first 5 rows)
5. Click "Validate SMILES"
6. Review validation results (valid/invalid count)
7. Click "Import X Materials"
8. Success! Redirected to materials page

**Tips:**
- Column names like "smiles", "SMILES", "structure" are auto-detected
- Invalid SMILES are skipped (you'll see the count)
- Duplicates are automatically skipped
- Max file size: 10MB

---

### 3. Property Predictions

**Predict for One Material:**

1. Click "Predictions" in navigation
2. Enter SMILES notation
3. Click "Predict Properties"
4. View results:
   - **Tg** - Glass transition temperature (°C)
   - **FFV** - Free volume fraction
   - **Tc** - Crystallinity temperature (K)
   - **Density** (g/cm³)
   - **Rg** - Radius of gyration (Å)

**Understanding Results:**
- Each property has a predicted value
- Confidence score shows prediction reliability
- Higher confidence = more reliable prediction

---

### 4. Data Quality Dashboard

**Access Quality Insights:**

1. Click "Quality" in navigation
2. View 3 sections:

**Completeness:**
- Bar chart showing % of materials with each property measured
- Helps identify gaps in your dataset

**Outliers:**
- Materials with unusual property values (Z-score > 3)
- Click to see examples
- Useful for finding data entry errors

**Distributions:**
- Histograms for each property
- Statistics: mean, median, std deviation, range
- Understand your dataset's characteristics

---

### 5. Visualizations & Correlations

**Explore Relationships:**

1. Click "Visualizations" in navigation
2. View correlation matrix cards
3. Each card shows:
   - Two properties being compared
   - Correlation coefficient (r)
   - P-value (significance)
   - Number of data points

**Interpret Correlations:**
- **r > 0.7**: Strong positive correlation (green)
- **r > 0.4**: Moderate correlation (yellow)
- **r < 0.4**: Weak correlation (gray)
- **p < 0.05**: Statistically significant (blue badge)

**Interactive Scatter Plot:**
1. Click any correlation card → View scatter plot
2. Or use dropdown menus to select X and Y properties
3. Hover over points to see material names
4. View correlation statistics above chart

---

### 6. AI Research Assistant (Chat)

**Start a Conversation:**

1. Click "Chat" in navigation
2. Optional: Click a suggested prompt for quick start
3. Or type your own question
4. Press Enter or click "Send"
5. Get AI response (currently in mock mode)

**What You Can Ask:**

**Property Questions:**
- "What is the glass transition temperature of polystyrene?"
- "Predict properties for SMILES: c1ccccc1"

**Data Analysis:**
- "Analyze the materials in the database"
- "What are the outliers in my dataset?"

**Literature:**
- "Find research papers on polymer synthesis"
- "What's the latest on polymer glass transitions?"

**Synthesis:**
- "How do I synthesize polyethylene?"
- "What's the best route for making polystyrene?"

**Recommendations:**
- "Recommend materials similar to polycarbonate"
- "What polymer has high Tg and low density?"

**Manage Conversations:**
- **New Chat**: Click "+ New Chat" button
- **Switch**: Click conversation in sidebar
- **Delete**: Click X button next to conversation

**Note:** Currently using mock AI responses. Upgrade to real Claude API for intelligent answers.

---

### 7. Search & Export

**Advanced Search:**

Materials page supports filtering by:
- **Property ranges**: Find materials with Tg > 400K
- **Name**: Search by material name
- **SMILES**: Substring search in SMILES

**Export Data:**

1. Navigate to Materials page
2. Apply any filters (optional)
3. Choose format:
   - **Export CSV** - Plain text, universal
   - **Export Excel** - Formatted with auto-sized columns
4. File downloads automatically

**Export includes:**
- All material data
- SMILES (original + canonical)
- All measured properties
- Chemistry features
- Timestamps

---

## Tips & Best Practices

### Data Entry
- ✅ Use canonical SMILES when possible
- ✅ Include property units in column names
- ✅ Validate SMILES before bulk import
- ❌ Don't mix different polymer types without noting
- ❌ Don't include headers in multiple rows

### Property Predictions
- ✅ Cross-reference with experimental data
- ✅ Check confidence scores
- ✅ Use for screening, not final design
- ❌ Don't rely solely on predictions
- ❌ Don't predict for very large polymers (>1000 atoms)

### Data Quality
- ✅ Review outliers regularly
- ✅ Aim for >80% completeness
- ✅ Document measurement methods
- ❌ Don't ignore persistent outliers
- ❌ Don't mix measurement units

### Visualizations
- ✅ Look for significant correlations (p < 0.05)
- ✅ Consider physical meaning
- ✅ Use for hypothesis generation
- ❌ Don't assume correlation = causation
- ❌ Don't ignore low correlation if meaningful

---

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter` - Send chat message
- `Esc` - Close modal/dialog
- `Tab` - Navigate form fields

---

## Troubleshooting

### "Failed to fetch" Error
**Solution:** Backend may not be running. Check with admin.

### SMILES Not Validating
**Problem:** Invalid chemical structure
**Solution:** 
- Check for typos in SMILES
- Verify structure is chemically valid
- Use online SMILES validators

### Predictions Seem Wrong
**Problem:** ML model limitations
**Solution:**
- Check confidence score
- Verify SMILES is correct
- Compare with known compounds
- Note: Model trained on specific polymer types

### Can't Upload File
**Problem:** File too large or wrong format
**Solution:**
- Max size: 10MB
- Supported: .csv, .xlsx, .xls
- Check SMILES column exists

### Chat Not Responding
**Problem:** Backend connection
**Solution:**
- Refresh page
- Check browser console for errors
- Contact admin if persistent

---

## Data Privacy

- All data stored locally in your database
- No data sent to external services (except Claude API if enabled)
- CSV uploads are not permanently stored
- Conversation history saved in SQLite database

---

## Support

**Common Issues:**
- Check browser console (F12) for errors
- Clear browser cache and refresh
- Verify all services are running

**Need Help?**
- Check documentation: `/docs/` folder
- Review example CSV: `/tests/fixtures/sample_materials.csv`
- Contact development team

---

## Next Steps

**Beginner:**
1. Add 5-10 materials manually
2. Predict properties for a known polymer
3. Upload a small CSV file
4. Explore the quality dashboard

**Intermediate:**
1. Upload 100+ materials from CSV
2. Analyze correlations
3. Identify and fix outliers
4. Export refined dataset

**Advanced:**
1. Integrate with LIMS
2. Set up automated imports
3. Custom ML model training
4. API integration with other tools

---

**Happy Researching!** 🧪✨
