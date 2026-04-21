# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Analysis of the **Encuesta de Acceso y Usos de Internet (EAUI)** — Chile's national internet access and usage survey published by SUBTEL (Subsecretaría de Telecomunicaciones). The repo covers 8 independent cross-sectional survey waves (2012, 2013, 2015–2018, 2024–2025) plus an in-progress 2026 wave.

The analytical goal is to explain structural determinants of internet access (not longitudinal tracking) using demographic, socioeconomic, and territorial variables, explicitly excluding technological proxies (`tipo_acceso`, `usa_computador`, `usa_smartphone`) that would be tautological.

## Running the Notebooks

Notebooks run in Jupyter. No build or test pipeline exists — execution order within each notebook matters.

```bash
# Start Jupyter
jupyter notebook

# Or directly open a specific notebook
jupyter notebook eaui2026_v2.ipynb
```

Key dependency: `pyreadstat` for reading `.sav` (SPSS) files.

## Notebook Architecture

### `eaui2026_v2.ipynb` — Active notebook for 2026 data

Cells must be executed in order (sections 1–10 are setup; section 11+ is analysis):

| Section | What it does |
|---------|-------------|
| 1. Carga | Reads `data/sav/2026.sav` via `pyreadstat`, 5,000 rows × 587 columns |
| 2. GSE derivado | Derives socioeconomic group (`gse`: E→AB) from `A10` (education) + `A11` (occupation of household head) — must run before any renaming |
| 3. Etiquetas limpias | Builds `etiquetas_limpias` dict from SPSS metadata, stripping code prefixes |
| 4. Diccionario | Searchable variable dictionary from `meta.column_names` / `meta.column_labels` |
| 5. NS/NR | Replaces `9999999` sentinel values with `NaN` in money/amount columns |
| 6. Renombrado | Maps 53 SPSS codes (e.g. `COD_REGION`, `Q1_2`) to short readable names (e.g. `region`, `sexo`) |
| 7. Recodificaciones | Overwrites numeric codes with text labels in-place (no `_rec` suffix) |
| 8. Ingreso del hogar | Derives continuous income (`ingreso_pm`) from banded income codes (vary by household size), then creates `ingreso_tramo` and `ingreso_grupo` |
| 9. Funciones de análisis | Defines `ORDEN_CATEGORIAS`, `fordf()`, `dstats()` |
| 10. Grupos RM | Defines `GRUPOS_RM` dict and `analizar_rm()` / `analizar_rm_cruce()` functions |

### Core analysis functions (defined in section 9–10)

**`dstats(data_df, variables, tipo, cruce, factor, transponer, estilo)`**
- `tipo='frecuencia'` — weighted frequency table for one variable
- `tipo='cruzada'` — cross-tabulation of one variable by `cruce`
- `tipo='promedio'` or `'suma'` — weighted mean/sum, optionally by `cruce`
- `factor`: weighting column — use `'fe_hogar'` for household-level vars, `'fe_personas'` for individual-level vars
- `estilo=False` returns a plain DataFrame instead of a styled Styler

**`analizar_rm(grupo, factor, top_n, estilo)`** — weighted analysis of a multiple-response group (defined in `GRUPOS_RM`)

**`analizar_rm_cruce(grupo, cruce, factor, estilo)`** — multiple-response group crossed by a demographic variable

## Key Variable Conventions

- Weighting columns: `fe_hogar` (household weight), `fe_personas` (person weight), `pond_hogar`, `pond_personas`
- All recoded variables use text labels directly (e.g. `'Hombre'/'Mujer'`, `'Urbana'/'Rural'`), never numeric codes after section 7
- `ORDEN_CATEGORIAS` dict controls display ordering for all categorical variables
- GSE categories ordered: `E → D → C3 → C2 → C1 → AB` (low to high)

## Data Files

- `data/sav/` — SPSS source files (authoritative), one per year including `2026.sav`
- `data/csv/` — CSV exports; `df_final_muestra.csv` is the combined multi-year analysis sample
- `data/xlsx/` — Excel exports
- `diccionario_variables.csv` — column-level metadata (name, type, unique count, nulls)
