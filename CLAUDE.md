# CLAUDE.md — eaui_subtel

**Project:** EAUI Subtel 2026 Data Processing & Analysis  
**Tech Stack:** Python / Jupyter / Pandas / Numpy  
**Data:** SPSS (.sav), CSV, Excel | 5,000 cases × 587 variables  
**Expansion factors:** fe_personas (person-level), fe_hogar (household-level)

## Quick Start

```bash
# Activate environment
source ~/.pyenv/versions/datascience/bin/activate

# Start Jupyter
jupyter notebook

# Open main notebook
# → eaui2026_v3.ipynb (latest)
```

## Project Structure

```
.
├── eaui2026_v*.ipynb          # Main processing notebooks (v3 is latest)
├── data/
│   ├── sav/                   # Raw SPSS files (2008–2026)
│   ├── csv/                   # CSV exports
│   └── xlsx/                  # Excel files
├── docs/
│   ├── informe_final.pdf      # Final analysis report
│   ├── PLAN_ANALISIS_EAUI2026.md
│   ├── PLAN_UNIVARIADO_EAUI2026.md
│   └── ...
├── analysis/
│   ├── documentation/         # Model docs, analysis guides
│   └── ...
├── diccionario_variables.csv  # Data dictionary
└── .claude-os/                # Claude OS config
```

## Data Dictionary

`diccionario_variables.csv` defines all columns:
- `nombre_columna` — final column name
- `tipo_datos` — Python dtype
- `valores_unicos` — cardinality
- `null_count` — missing values
- `descripcion` — variable description

Load it:
```python
import pandas as pd
diccionario = pd.read_csv('diccionario_variables.csv')
```

## Processing Pipeline

1. **Load** — `pyreadstat.read_sav()` → pandas DataFrame
2. **Derive GSE** — calculate socioeconomic variables (uses SPSS column names: A10, A11, etc.)
3. **Recode** — normalize text, handle missing values
4. **Export** — save to CSV or use for analysis
5. **Report** — generate informe_final.pdf

## Key Libraries

- `pyreadstat` — read/write SPSS `.sav`
- `pandas` — data frames & manipulation
- `numpy` — numeric ops
- `re`, `unicodedata` — text normalization

Install:
```bash
pip install pyreadstat pandas numpy
```

## Notebook Workflow

Notebooks are **source of truth** for processing logic. Always:
1. Keep notebooks **top-to-bottom reproducible** ("Restart & Run All")
2. Use **expansion factors** in weighted calculations: `fe_personas`, `fe_hogar`
3. Reference **SPSS column names** (A10, A11) in comments when deriving GSE
4. Save **derived data** to separate paths (never overwrite raw `/data/sav/`)

## Claude OS Integration

Claude OS provides:
- **Structural Index** — instant codebase map (tree-sitter)
- **Semantic Search** — "How does GSE derivation work?"
- **Project Memory** — saves decisions, patterns, architecture
- **Knowledge Docs** — all `/docs` and `/analysis/documentation` indexed

Use:
```
/claude-os-search — search project
/claude-os-save — save insight
/claude-os-session — manage work sessions
/claude-os-remember — quick save
```

## Agent-OS

8 specialized agents available for structured development:
- **Product** — gather requirements
- **Specs** — create detailed specifications
- **Standards** — backend/frontend/global/testing guides
- **Implementation** — code generation with verification

Activate: "I'm using Agent-OS to implement this feature"

## Common Tasks

**View data:**
```python
import pyreadstat
df, meta = pyreadstat.read_sav('data/sav/2026.sav')
df.head()
df.info()
```

**Apply expansion factor (person-level):**
```python
# Weighted aggregation
df.groupby('variable').size() * df['fe_personas']
```

**Update from SPSS:**
When raw SPSS files change, re-run notebook top-to-bottom to rebuild datasets.

## Rules for Claude

- Use Jupyter MCP for notebook operations (read, edit, insert, execute)
- **Never modify raw `/data/sav/` files** — write to separate path
- Execute cells to verify — don't assume correctness
- Large outputs consume tokens — prefer `.head()`, `.shape`
- Notebooks must be reproducible: "Restart & Run All" always works
- Expansion factors matter: always use `fe_personas` or `fe_hogar` in weighted calcs

## Documentation

- **docs/** — reports, analysis plans, dashboards
- **analysis/documentation/** — model guides, SHAP analysis, insights
- All indexed in Claude OS knowledge base
