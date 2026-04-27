# Coding Conventions

**Analysis Date:** 2026-04-27

## Overview

This is a data analysis Jupyter notebook project focused on the EAUI (Encuesta de Acceso y Usos de Internet). Code consists primarily of sequential data processing and visualization cells in `eaui2026_v2.ipynb`. No formal linting, type checking, or formatting tools are configured.

## Naming Patterns

**Variables (DataFrame columns):**
- Lowercase with underscores: `acceso_internet_hogar`, `educ_grupo`, `pago_mensual_internet`
- Short, descriptive names after renaming (section 6): `sexo` instead of `Q1_2`, `region` instead of `COD_REGION`
- Derived variables follow parent naming: `educ_grupo` (derived from `educ`), `ingreso_grupo` (derived from `ingreso_tramo`)
- Recoded categories stored in-place (no `_rec` suffix): `sexo` column contains `'Hombre'`/`'Mujer'` after section 7
- Weight columns: `fe_hogar`, `fe_personas`, `pond_hogar`, `pond_personas` (fixed SPSS names)

**Dictionaries & Mappings:**
- Prefixed with underscore for internal use: `_mapa_educ`, `_mapa_ocup`, `_M` (GSE matrix)
- Uppercase with underscores for module-level constants: `ORDEN_CATEGORIAS`, `GRUPOS_RM`, `PALETA`, `ETIQ_VAR`
- Short variable codes in square brackets: `Q8_BASICO`, `Q8_INTERMEDIO`, `Q8_AVANZADO` (digital skills hierarchy)
- Tuple keys for matrix-style lookups: `_M = {(occupation_code, education_level): gse_category}`

**Functions:**
- Lowercase with underscores: `fordf()`, `dstats()`, `analizar_rm()`, `analizar_rm_cruce()`
- Underscore prefix for internal helpers: `_educ_g()`, `_ordenar()`, `_wavg()`, `_wsum()`, `_parse_idx()`, `_nivel()`
- Generator functions prefixed with underscore: `_cols_b`, `_cols_i`, `_cols_a` (column lists for Q8 items)

**Code Blocks & Markdown Sections:**
- Markdown cells describe section purpose with numbering: `## 1. Carga del archivo`, `## 9. Funciones de análisis ponderado`
- Comments in Spanish (project language): `# Análisis`, `# Recodificación de educ_jh y ocupacion_jh`
- Long comments use `# ──` visual separator: `# ── Variables para el ACM ────────────────────────────────────────────────────`

## Code Style

**Formatting:**
- No automated formatter configured (black, ruff, prettier)
- Indentation: 4 spaces (Python standard)
- Line breaks: Long function signatures broken across lines, arguments aligned
- Imports grouped: stdlib first, then external libraries (not enforced, but observed)
  ```python
  import pyreadstat
  import re
  import unicodedata
  import pandas as pd
  import numpy as np
  ```

**Linting:**
- No formal linter configured (.pylintrc, .flake8, ruff.toml absent)
- Code relies on manual review and Jupyter cell-by-cell validation
- Common issues not flagged: unused variables, long lines, bare `except` clauses

**DataFrames:**
- Use `.copy()` when modifying: `df = df.copy()` before in-place transformations (section 7)
- Use `.dropna()` for complete-case analysis: `df_acm = df.loc[mask_q8, VAR_ACM].dropna().copy()`
- Categorical variables created explicitly: `df['gse'] = pd.Categorical(..., categories=..., ordered=True)`
- String values preferred over codes after section 7: use `'Sí'`/`'No'` not `1`/`2`

**Vectorized Operations:**
- Prefer `.apply()` for row-wise transformations: `df['nivel_habilidades'] = df.apply(_nivel, axis=1)`
- Use `.map()` for value replacements: `df['sexo'] = df['sexo'].map({1:'Hombre', 2:'Mujer'})`
- `.groupby()` with aggregation for weighted statistics: `df.groupby(var, observed=True)[factor].sum()`

## Import Organization

**Order (observed in notebook):**
1. Data I/O: `pyreadstat` (SPSS), `pandas`, `numpy`
2. String handling: `re`, `unicodedata`
3. Visualization: `seaborn`, `matplotlib.pyplot`, `matplotlib.patches`, `plotly.express`
4. Analysis: `prince` (MCA)

```python
import pyreadstat
import re
import unicodedata
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import prince
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
```

**No path aliases configured** — all imports are direct.

## Error Handling

**Strategy:** Minimal explicit error handling. Reliance on assertion via printouts and manual cell validation.

**Patterns observed:**
- Value validation via `.value_counts()` and `.describe()` after transformations:
  ```python
  print('GSE:', df['gse'].value_counts().reindex(_ORDEN_GSE).to_dict())
  ```
- Dtype validation implicit: `.astype(str)` before MCA fitting to ensure all columns are strings
- Sentinel value replacement (not error handling): `df[col].replace(9999999, np.nan)` for NS/NR codes
- No try/except blocks in data processing — failures are visible immediately in notebook

**Data Quality Checks:**
- Weights validation via `.sum()`: `base = df.groupby(cruce, observed=True)[factor].sum()`
- Missing values handled upstream in `dstats()`: `.dropna()` called inside analysis function
- Categorical mask creation to filter respondents: `mask_q8 = df[_cols_q8].notna().any(axis=1)`

## Logging

**Framework:** Console output via `print()` — no logging library configured.

**Patterns:**
- Section summaries print count/column info:
  ```python
  print(f"Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")
  ```
- Key operations confirm completion:
  ```python
  print('GSE:', df['gse'].value_counts().reindex(_ORDEN_GSE).to_dict())
  print('Recodificaciones completadas.')
  ```
- Analysis functions return styled HTML tables (Styler) with title captions as documentation:
  ```python
  titulo = f"Frecuencia: '{var}' — base ponderada: {tot:,.0f} ({factor})"
  return fordf(res, titulo=titulo)
  ```

## Comments & Documentation

**When to Comment:**
- Non-obvious logic: GSE derivation matrix (`_M = {...}`)
- Data validation intent: `# Validación: promedio de ingreso debe subir de E a AB`
- Section boundaries and purposes marked in markdown cells (structured documentation)
- Transformation intent before complex operations: `# Recodificación de educ_jh y ocupacion_jh (aquí, con valores numéricos aún intactos)`

**JSDoc/Docstrings:**
- Functions include single-line docstrings:
  ```python
  def fordf(df_tabla, titulo=None):
      """Formato visual: enteros sin decimales, porcentajes con 1 decimal."""
  ```
- Core analysis functions (`dstats`, `analizar_rm`) include multi-line docstrings with parameter descriptions:
  ```python
  def dstats(data_df, variables, tipo='frecuencia', cruce=None, factor=None, transponer=False, estilo=True):
      """
      Análisis ponderado de variables simples.
      tipo: 'frecuencia' | 'cruzada' | 'promedio' | 'suma'
      Si estilo=True, retorna Styler formateado. Si es False, retorna el DataFrame puro.
      """
  ```
- Parameter documentation via examples at function call site:
  ```python
  # Ejemplos de uso de generar_grafico
  generar_grafico('sexo', factor='fe_personas', titulo='Distribución de sexo')
  ```

**Language:** Spanish (project language). All comments and docstrings in Spanish.

## Function Design

**Size Guidelines:**
- Small helper functions: `_educ_g()` (4 lines), `_wavg()` (3 lines), `_nivel()` (5 lines)
- Mid-level functions: `_ordenar()` (10 lines), `fordf()` (12 lines)
- Complex functions: `dstats()` (60+ lines with multiple branches), `generar_grafico()` (70+ lines)

**Parameters:**
- Positional for primary data: `dstats(data_df, variables, tipo, ...)`
- Keyword with defaults for optional settings: `factor=None, estilo=True, cruce=None`
- Use tuple unpacking for structured data: `desc, cols = GRUPOS_RM[grupo]`

**Return Values:**
- Styled Pandas Styler object (HTML output): `fordf()`, `dstats(..., estilo=True)`
- Plain DataFrame for downstream processing: `dstats(..., estilo=False)`
- Figure and axes tuple for matplotlib: `fig, ax = plt.subplots(...)`
- None for print-only operations: visualization functions `plt.show()` implicitly return None

## Module Design

**Exports (Module-Level):**
- Core dictionaries for reuse: `ORDEN_CATEGORIAS`, `GRUPOS_RM`, `PALETA`, `ETIQ_VAR`
- Core functions: `fordf()`, `dstats()`, `analizar_rm()`, `analizar_rm_cruce()`, `generar_grafico()`, `crear_grafico_interactivo()`
- DataFrame `df` is the main shared state (loaded in section 1, transformed through sections 2–8)

**Barrel Files:** Not applicable — Jupyter notebook structure, not modular Python.

**Global State:** 
- Single DataFrame `df` modified in place across sections
- Module-level constants: `ORDEN_CATEGORIAS` (defined section 9), `GRUPOS_RM` (section 10), `PALETA`, `ETIQ_VAR` (section 30)
- No class definitions; pure functional style with shared mutable state

## Testing & Validation in Code

**Inline Assertions:**
- Value distribution checks: `print(df['gse'].value_counts().reindex(_ORDEN_GSE).to_dict())`
- Income coherence validation: 
  ```python
  df.groupby('gse', observed=True)['ingreso_pm'].agg(N='count', Promedio='mean').reindex(_ORDEN_GSE)
  ```
- Base counts after masking: `mask_q8 = df[_cols_q8].notna().any(axis=1)` → `base_q8 = int(mask_q8.sum())`

**Output Validation:**
- Human review of printed statistics after each major transformation
- Jupyter cell execution order mandatory; failure blocks downstream cells

---

*Convention analysis: 2026-04-27*
