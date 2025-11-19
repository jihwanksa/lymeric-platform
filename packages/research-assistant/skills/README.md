# Research Assistant Skills

This directory contains custom Claude Skills for the Lymeric Research Assistant, providing domain expertise in materials science and polymer chemistry.

## Skills Overview

### 1. Polymer Property Expert (`polymer_property_expert/`)
**Purpose:** Expert knowledge on polymer physics and structure-property relationships

**Capabilities:**
- Explain how molecular structure affects Tg, density, FFV, Tc, Rg
- Provide typical property ranges for polymers
- Suggest structural modifications for desired properties
- Interpret experimental data

### 2. SMILES Chemistry Expert (`smiles_chemistry_expert/`)
**Purpose:** Interpret and analyze SMILES molecular representations

**Capabilities:**
- Parse SMILES notation
- Identify functional groups
- Explain molecular structure from SMILES
- Suggest SMILES modifications

### 3. Experimental Design Assistant (`experimental_design/`)
**Purpose:** Design experiments using DOE principles

**Capabilities:**
- Generate factorial designs
- Suggest optimal sampling strategies
- Recommend controls and replicates

### 4. Data Analysis Expert (`data_analysis/`)
**Purpose:** Generate Python code for data analysis

**Capabilities:**
- Correlation analysis
- Feature importance plots
- Statistical tests
- Visualization generation

### 5. Literature Expert (`literature_expert/`)
**Purpose:** Polymer science knowledge from literature

**Capabilities:**
- Explain polymer chemistry terminology
- Cite typical property ranges
- Suggest research directions

## Usage

Skills are loaded automatically by the Claude Skills service when the Research Assistant backend starts. Each skill directory contains:

- `skill.yaml` - Skill metadata (name, description, version)
- `instructions.md` - Detailed domain instructions for Claude
- `examples/` - Few-shot examples (optional)
- `tools/` - Optional Python utilities (optional)

## Integration with Claude

When Claude Skills API access is available, skills are registered using:

```python
from anthropic.lib import files_from_dir

skill = client.beta.skills.create(
    display_title="Polymer Property Expert",
    files=files_from_dir("./polymer_property_expert"),
    betas=["skills-2025-10-02"]
)
```

Then used in chat:

```python
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    betas=["skills-2025-10-02"],
    container={
        "skills": [
            {"type": "custom", "skill_id": skill.id, "version": "latest"}
        ]
    },
    messages=[{"role": "user", "content": "Why does Tg increase with aromatic rings?"}]
)
```

## Development

To add a new skill:
1. Create directory: `skills/new_skill_name/`
2. Add `skill.yaml` with metadata
3. Write `instructions.md` with domain knowledge
4. Update `claude_service.py` to register the skill

## Status

**Current:** Skill definitions created, waiting for Claude Skills beta API access
**Next:** Test Skills integration when API key is available
