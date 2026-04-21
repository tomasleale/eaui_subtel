# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Analysis of the **Encuesta de Acceso y Usos de Internet (EAUI)** — Chile's national internet access and usage survey published by SUBTEL (Subsecretaría de Telecomunicaciones). The repo covers 8 independent cross-sectional survey waves (2012, 2013, 2015–2018, 2024–2025) plus an in-progress 2026 wave.

The analytical goal is to explain structural determinants of internet access (not longitudinal tracking) using demographic, socioeconomic, and territorial variables, explicitly excluding technological proxies (`tipo_acceso`, `usa_computador`, `usa_smartphone`) that would be tautological.

## Running the Notebooks

Notebooks run in Jupyter. No build or test pipeline exists — execution order within each notebook matters.

```bash
jupyter notebook eaui2026_v2.ipynb
```

Key dependencies: `pyreadstat` (read `.sav` SPSS files), `prince` (MCA / multiple correspondence analysis).

## Notebooks

- **`eaui2026_v2.ipynb`** — Active notebook. Sections 1–10 are setup; section 11+ is analysis.
- **`eaui2026.ipynb`** — Older draft, superseded by v2. Do not use as the reference.

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

## Key Variable Conventions

- Weighting columns: `fe_hogar` (household weight), `fe_personas` (person weight), `pond_hogar`, `pond_personas`
- All recoded variables use text labels directly (e.g. `'Hombre'/'Mujer'`, `'Urbana'/'Rural'`), never numeric codes after section 7
- `ORDEN_CATEGORIAS` dict controls display ordering for all categorical variables
- GSE categories ordered: `E → D → C3 → C2 → C1 → AB` (low to high)
- Derived variables added in section 7: `educ_grupo` (`'Básica o menos'/'Media'/'Superior'`), `tramo_edad` (`'Menor de 18'`…`'60 y más'`)
- `nivel_habilidades` derived in section 11 from Q8 columns: hierarchical — Avanzado > Intermedio > Básico > Sin habilidades

## Data Files

- `data/sav/` — SPSS source files (authoritative), one per year including `2026.sav`
- `data/csv/` — CSV exports; `df_final_muestra.csv` is the combined multi-year analysis sample
- `data/xlsx/` — Excel exports
- `diccionario_variables.csv` — column-level metadata (name, type, unique count, nulls)

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
