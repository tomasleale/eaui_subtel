# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EAUI Subtel** is a data processing and analysis project for the EAUI 2026 survey (Encuesta de Acceso y Uso de Internet). It loads, recodes, and prepares telecommunications survey data from multiple formats (SPSS `.sav`, CSV, Excel).

**Primary work:** Jupyter notebooks in root directory
- `eaui2026_v3.ipynb` — latest version, main processing pipeline
- `eaui2026_v2.ipynb`, `eaui2026.ipynb` — earlier versions

**Data:** `/data/` directory contains survey data in multiple formats:
- `/data/sav/` — SPSS format files (2008–2026)
- `/data/csv/` — CSV exports
- `/data/xlsx/` — Excel exports
- `diccionario_variables.csv` — data dictionary defining all columns

**Output:** `/docs/informe_final.pdf` — final analysis report

## Python Dependencies

Primary libraries (inferred from notebook imports):
- `pyreadstat` — read SPSS `.sav` files
- `pandas` — data manipulation
- `re`, `unicodedata` — text normalization

Install via:
```bash
pip install pyreadstat pandas
```

## Working with Notebooks

Run Jupyter locally:
```bash
jupyter notebook
```

Then open `eaui2026_v3.ipynb` in the browser.

The notebook is organized into sections:
1. **Load file** — reads SPSS data via `pyreadstat`
2. **Derive GSE** — calculates derived socioeconomic variables (uses original SPSS column names like `A10`, `A11`)
3. Additional data processing and recoding sections follow

## Data Flow

1. Raw data in `/data/sav/` (SPSS format)
2. Load via `pyreadstat.read_sav()` → pandas DataFrame
3. Recode variables (GSE derivation, text normalization, etc.)
4. Output to CSV or used for analysis
5. Generate report (`docs/informe_final.pdf`)

## Key Variable Definitions

See `diccionario_variables.csv` for the data dictionary:
- `nombre_columna` — column name in final dataset
- `tipo_datos` — Python dtype
- `valores_unicos` — cardinality
- `null_count` — missing values
- `descripcion` — variable description

## Git & Version Control

Active branch: `main`  
Remote: origin

The `.git/hooks/` directory contains custom hooks (`pre-commit`, `post-checkout`, `post-commit`) — inspect if automated behavior seems unexpected.

## Common Tasks

**View data structure:**
```python
# In notebook or Python REPL
import pyreadstat
df, meta = pyreadstat.read_sav('data/sav/2026.sav')
df.head()
df.info()
```

**Load variable dictionary:**
```python
diccionario = pd.read_csv('diccionario_variables.csv')
```

**Update from SPSS:**
When raw SPSS files change, re-run the full notebook to rebuild processed datasets.

## Rules for Claude when working with Jupyter notebooks

### Tool preference
- Use the Jupyter MCP for all `.ipynb` operations — read, edit, insert, delete, execute.
- Do not use your built-in `NotebookEdit` tool; it writes source as a single JSON string, which ruins standard Jupyter formatting.

### Outputs
- Never print secrets, API keys, tokens, or passwords into cell output.
- Large outputs consume tokens and fill up your context window. Prefer summaries (`.head()`, `.shape`) over dumping full DataFrames.

### Execution
- When installing packages, use `%pip install` inside the notebook (not `!pip install`) so packages install into the running kernel.
- Execute cells to verify they work. Do not assume the code is correct.
- If a cell errors, read the actual traceback before attempting a fix. Do not guess.

### State and reproducibility
- Jupyter kernels are stateful. A notebook that runs top-to-bottom after "Restart & Run All" is the only notebook that works — verify this before declaring a task done.

### Data safety
- Do not modify or delete raw data files. Write derived data to a separate path.
