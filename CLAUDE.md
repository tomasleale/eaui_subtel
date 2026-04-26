# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Analysis of the **Encuesta de Acceso y Usos de Internet (EAUI)** — Chile's national internet access and usage survey published by SUBTEL (Subsecretaría de Telecomunicaciones). The repo covers 8 independent cross-sectional survey waves (2012, 2013, 2015–2018, 2024–2025) plus an in-progress 2026 wave.

The analytical goal is to explain structural determinants of internet access (not longitudinal tracking) using demographic, socioeconomic, and territorial variables, explicitly excluding technological proxies (`tipo_acceso`, `usa_computador`, `usa_smartphone`) that would be tautological.

## Setup

**Python Requirements:**
- Python 3.8+ (tested with 3.10+)
- Virtual environment recommended

**Install dependencies:**
```bash
pip install pyreadstat prince pandas numpy seaborn matplotlib plotly jupyter
```

**Verify setup:**
```bash
jupyter notebook eaui2026_v2.ipynb
# Run cell 1 (Carga) to verify data loads (should show "Filas: 5,000 | Columnas: 587")
```

## Running the Notebooks

Notebooks run in Jupyter. No build or test pipeline exists — **execution order within each notebook is mandatory**.

```bash
jupyter notebook eaui2026_v2.ipynb
```

**CRITICAL: Always execute sections 1–10 first** before any analysis. These sections load data, derive variables, and define analysis functions. Skipping or reordering breaks downstream cells.

Key dependencies: `pyreadstat` (read `.sav` SPSS files), `prince` (MCA / multiple correspondence analysis).

## Notebooks

- **`eaui2026_v2.ipynb`** — **Current production notebook.** Use this for all analysis. Sections 1–10 are setup; section 11+ is analysis.
- **`eaui2026.ipynb`** — Archived draft. Reference only if investigating historical decisions; do not use for active analysis.

## Notebook Architecture — `eaui2026_v2.ipynb`

Cells must be executed in order:

| Section | What it does |
|---------|-------------|
| 1. Carga | Reads `data/sav/2026.sav` via `pyreadstat`, 5,000 rows × 587 columns |
| 2. GSE derivado | Derives `gse` (E→AB) from `A10` (education) + `A11` (occupation of household head) — must run before renaming |
| 3. Etiquetas limpias | Builds `etiquetas_limpias` dict from SPSS metadata, stripping code prefixes |
| 4. Diccionario | Searchable variable dictionary from `meta.column_names` / `meta.column_labels` |
| 5. NS/NR | Replaces `9999999` sentinel values with `NaN` in money/amount columns |
| 6. Renombrado | Maps 53 SPSS codes (e.g. `COD_REGION`, `Q1_2`) to short readable names (e.g. `region`, `sexo`) |
| 7. Recodificaciones | Overwrites numeric codes with text labels in-place (no `_rec` suffix); also derives `educ_grupo` and `tramo_edad` |
| 8. Ingreso del hogar | Derives continuous income (`ingreso_pm`) from banded income codes (vary by household size), then creates `ingreso_tramo` and `ingreso_grupo` |
| 9. Funciones de análisis | Defines `ORDEN_CATEGORIAS`, `fordf()`, `dstats()` |
| 10. Grupos RM | Defines `GRUPOS_RM` dict (25 multiple-response groups) and `analizar_rm()` / `analizar_rm_cruce()` |
| 11+ | Analysis — e.g. section 11 classifies Q8 digital skills into `nivel_habilidades` (Básico / Intermedio / Avanzado / Sin habilidades) using `Q8_BASICO`, `Q8_INTERMEDIO`, `Q8_AVANZADO` dicts, then runs MCA with `prince` |

## Core Analysis Functions (sections 9–10)

**`fordf(df_tabla, titulo)`** — applies visual styling: integer format for weighted counts, 1-decimal for percentages. Returns a `Styler`. All `dstats`/`analizar_rm` functions call this when `estilo=True`.

**`dstats(data_df, variables, tipo, cruce, factor, transponer, estilo)`**
- `tipo='frecuencia'` — weighted frequency table for one variable
- `tipo='cruzada'` — cross-tabulation of one variable by `cruce`
- `tipo='promedio'` or `'suma'` — weighted mean/sum, optionally by `cruce`
- `factor`: weighting column — use `'fe_hogar'` for household-level vars, `'fe_personas'` for individual-level vars
- `estilo=False` returns a plain DataFrame instead of a styled Styler

**`analizar_rm(grupo, factor='fe_hogar', top_n, estilo)`** — weighted analysis of a multiple-response group key from `GRUPOS_RM`

**`analizar_rm_cruce(grupo, cruce, factor='fe_personas', estilo)`** — multiple-response group crossed by a demographic variable

## Weighting Guide

All analysis functions support weighted calculation via the `factor` parameter. Choose the correct weight for your variable's scope:

| Weight | Use for | Example |
|--------|---------|---------|
| `fe_hogar` | Household-level variables | `acceso_internet_hogar`, `pago_mensual_internet`, `ingreso_hogar` |
| `fe_personas` | Individual/person-level variables | `sexo`, `edad`, `educ`, `uso_computador`, `actividad` |
| `pond_hogar` | Household-level, normalized | Alternative to `fe_hogar`; used in probability models |
| `pond_personas` | Individual-level, normalized | Alternative to `fe_personas`; used in probability models |

**Default behavior:** `dstats()` defaults to `factor=None` — must always specify. `analizar_rm()` defaults to `factor='fe_hogar'`. Use `factor='fe_personas'` when analyzing individual responses (e.g., digital skills Q8, individual internet use).

## Common Analysis Patterns

**Frequency distribution (one variable):**
```python
dstats(df, 'sexo', tipo='frecuencia', factor='fe_personas', estilo=True)
```

**Cross-tabulation (variable by demographic):**
```python
dstats(df, 'acceso_internet_hogar', tipo='cruzada', cruce='gse', factor='fe_hogar', estilo=True)
```

**Weighted mean (e.g., average age by GSE):**
```python
dstats(df, 'edad', tipo='promedio', cruce='gse', factor='fe_personas', estilo=True)
```

**Multiple-response analysis (e.g., digital skills Q8):**
```python
analizar_rm('Q8', factor='fe_personas', top_n=10, estilo=True)
```

**Multiple-response crossed by demographic:**
```python
analizar_rm_cruce('A12', cruce='gse', factor='fe_personas', estilo=True)
```

## Key Variable Conventions

- Weighting columns: `fe_hogar` (household weight), `fe_personas` (person weight), `pond_hogar`, `pond_personas`
- All recoded variables use text labels directly (e.g. `'Hombre'/'Mujer'`, `'Urbana'/'Rural'`), never numeric codes after section 7
- `ORDEN_CATEGORIAS` dict controls display ordering for all categorical variables
- GSE categories ordered: `E → D → C3 → C2 → C1 → AB` (low to high)
- Derived variables added in section 7: `educ_grupo` (`'Básica o menos'/'Media'/'Superior'`), `tramo_edad` (`'Menor de 18'`…`'60 y más'`)
- `nivel_habilidades` derived in section 11 from Q8 columns: hierarchical — Avanzado > Intermedio > Básico > Sin habilidades

## Data Files

Located in `data/` directory:
- `data/sav/` — SPSS source files (authoritative), 11 files: 2008, 2011–2018, 2024–2026
- `data/xlsx/` — Excel exports of raw data (10 files covering main survey years)
- `data/2026_procesado.csv` — Processed 2026 data output
- `diccionario_variables.csv` — Column-level metadata (587 variables, searchable by name/type/nulls)

## Quick Reference

**Always ensure sections 1–10 executed before analysis:**
```python
# Check that core functions are defined:
help(dstats)  # Should show function signature
ORDEN_CATEGORIAS.keys()  # Should show all category orderings
len(GRUPOS_RM)  # Should be 25 multiple-response groups
```

**Common mistakes:**
- Forgetting to specify `factor` in `dstats()` → use `'fe_hogar'` for household-level, `'fe_personas'` for individual-level
- Using numeric codes after section 7 → use text labels only (e.g., `'Hombre'` not `1`)
- Analyzing before running section 2 (GSE derivation) → breaks dependent analyses
- Filtering the dataframe without recomputing weights → results won't sum to population totals

## Troubleshooting & Data Validation

**"NameError: name 'dstats' is not defined"** → Section 9 (Funciones de análisis) has not been executed. Run sections 1–10 in order.

**"KeyError: 'sexo'" or similar** → Variable does not exist or has not been renamed yet. Check section 6 (`nombres_cortos` dict) and confirm section 6 executed successfully.

**Weights not summing correctly** → Verify correct `factor` parameter:
  - Household-level analysis? Use `fe_hogar`
  - Person-level analysis? Use `fe_personas`
  - Check that df was not filtered; if filtered, weights may not sum to the full sample

**Missing values appearing in output** → NS/NR sentinels (`9999999`) may not have been replaced. Confirm section 5 executed. Additional `NaN` values from `dropna()` in analysis functions are expected.

**ACM plot missing categories** — Confirm `mask_q8` or equivalent filter is applied correctly in section 11. Complete cases (all variables present) are required for `prince.MCA`.

## Notebook Lifecycle

- **`eaui2026_v2.ipynb`** — Active production notebook. Sections 1–10 must execute without error before any analysis.
- **`eaui2026.ipynb`** — Deprecated draft. Do not use as the reference; all active work is in v2.

When modifying notebook structure:
1. Preserve section order (1–10 are setup; 11+ are analysis)
2. Do not insert cells that break dependency chains (e.g., renaming before GSE derivation)
3. Test full top-to-bottom execution before committing

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
