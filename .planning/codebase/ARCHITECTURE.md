# Architecture

**Analysis Date:** 2026-04-27

## System Overview

The EAUI codebase is a **Jupyter-based data analysis system** for analyzing Chile's national internet access and usage survey (Encuesta de Acceso y Usos de Internet). The architecture is a **sequential pipeline notebook** where execution order is mandatory. Data flows through discrete transformation phases, each building on the previous, toward exploratory and predictive analysis of digital access determinants.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      Data Input Layer (Raw SPSS)                        │
│                    `data/sav/2026.sav` (5,000 rows × 587 cols)          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │   Section 1–4: Load & Initialize     │
         │   `eaui2026_v2.ipynb` cells 1–8      │
         │   (Import, metadata extraction)      │
         └──────────────┬────────────────────────┘
                        │
         ┌──────────────┴────────────────────────┐
         │  Sections 5–8: Derive & Recode       │
         │  `eaui2026_v2.ipynb` cells 9–18      │
         │  (GSE, education, occupation,        │
         │   income, text labels)               │
         └──────────────┬────────────────────────┘
                        │
         ┌──────────────┴─────────────────────────────────┐
         │  Sections 9–10: Analytic Functions & Groups   │
         │  `eaui2026_v2.ipynb` cells 20–23              │
         │  (dstats(), analizar_rm(), ORDEN_CATEGORIAS) │
         └──────────────┬─────────────────────────────────┘
                        │
         ┌──────────────┴─────────────────────────────────┐
         │   Sections 11+: Analysis & Visualization      │
         │   `eaui2026_v2.ipynb` cells 25+               │
         │   (Cross-tabs, MCA, skill classification,    │
         │    interactive plots, regression)             │
         └──────────────┬─────────────────────────────────┘
                        │
         ┌──────────────┴──────────────────────────────────┐
         │      Output Layer: Visualizations & Tables     │
         │      (Matplotlib, Plotly HTML, styled Styler)  │
         └───────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| **Data Loading** | Reads SPSS binary file, extracts column names and value labels from metadata | `eaui2026_v2.ipynb`, cells 1–2 |
| **GSE Derivation** | Computes socioeconomic status from education + occupation of household head, before any renaming | `eaui2026_v2.ipynb`, cell 4 |
| **Label Cleaning** | Strips SPSS question codes from variable labels to create readable `etiquetas_limpias` dict | `eaui2026_v2.ipynb`, cell 6 |
| **NS/NR Handling** | Replaces sentinel value `9999999` with `NaN` in monetary columns | `eaui2026_v2.ipynb`, cell 12 |
| **Column Renaming** | Maps 53 SPSS codes to short readable names (e.g., `COD_REGION` → `region`) | `eaui2026_v2.ipynb`, cell 14 |
| **Recodification** | Overwrites numeric codes with text labels in-place (e.g., `sexo`: 1→'Hombre', 2→'Mujer') | `eaui2026_v2.ipynb`, cell 16 |
| **Income Derivation** | Maps income bands to continuous values (point estimates via band midpoints or upper bounds), derives income tranche and group | `eaui2026_v2.ipynb`, cell 18 |
| **Analysis Functions** | Provides weighted frequency tables, cross-tabulation, weighted means/sums via `dstats()` | `eaui2026_v2.ipynb`, cell 20 |
| **Multiple-Response Groups** | Defines 25 grouped response sets (e.g., Q8 digital skills, P3 access devices) with `analizar_rm()` | `eaui2026_v2.ipynb`, cell 22 |
| **Digital Skills Classification** | Hierarchical classification of Q8 responses into 4 skill levels (Avanzado/Intermedio/Básico/Sin habilidades) | `eaui2026_v2.ipynb`, cell 29 |
| **Multiple Correspondence Analysis** | Visualizes relationships between skill level and sociodemographics via `prince.MCA` | `eaui2026_v2.ipynb`, cell 30 |
| **Visualization Generators** | Creates static (matplotlib) and interactive (Plotly) bar/line/pie charts with proper weighting and ordering | `eaui2026_v2.ipynb`, cells 32, 35 |

## Pattern Overview

**Overall:** **Sequential Jupyter pipeline with mandatory section ordering**

**Key Characteristics:**
- **Linear dependency chain:** Sections 1–10 (setup) must execute before sections 11+ (analysis). Skipping or reordering breaks downstream references.
- **In-place data mutation:** Recodifications overwrite original numeric columns with text labels (no `_rec` or `_label` suffix).
- **Global state:** DataFrames (`df`, `meta`), weight columns, categorical orderings (`ORDEN_CATEGORIAS`), and grouped variables (`GRUPOS_RM`) are module-level singletons referenced across all analysis functions.
- **Weighted aggregation:** All tabulation functions (`dstats()`, `analizar_rm()`) support household or person-level weighting via `fe_hogar` or `fe_personas` columns.

## Layers

**Layer 1: Data Ingestion & Metadata Extraction**
- Purpose: Load raw SPSS file and extract variable definitions
- Location: `eaui2026_v2.ipynb`, cells 1–3
- Contains: `pyreadstat.read_sav()` call, `meta` object (column names, labels, value dictionaries)
- Depends on: `/Users/tomas/github/eaui_subtel/data/sav/2026.sav`
- Used by: All downstream layers

**Layer 2: Structural Variable Derivation**
- Purpose: Compute GSE, income point estimates, derived age/education groups before label recodification
- Location: `eaui2026_v2.ipynb`, cells 4, 18
- Contains: Lookup tables (`_M` for GSE mapping, `_rangos` for income bins), categorical conversions
- Depends on: Layer 1 (raw df)
- Used by: Layer 3, all analytical functions

**Layer 3: Data Cleaning & Standardization**
- Purpose: Rename columns, replace coded values with text labels, handle missing values, standardize data types
- Location: `eaui2026_v2.ipynb`, cells 6, 12, 14, 16
- Contains: `nombres_cortos` dict (53 mappings), label cleaning regex, recodification maps
- Depends on: Layer 2
- Used by: Layer 4

**Layer 4: Analytic Functions & Metadata**
- Purpose: Define weighting logic, category ordering, multiple-response groupings
- Location: `eaui2026_v2.ipynb`, cells 20–23
- Contains: `ORDEN_CATEGORIAS` dict (14 variables with display orderings), `GRUPOS_RM` dict (25 multiple-response groups), `dstats()`, `analizar_rm()`, `fordf()`, `_ordenar()`
- Depends on: Layer 3
- Used by: Layer 5 (analysis and visualization)

**Layer 5: Analysis & Insight Generation**
- Purpose: Exploratory analysis, segmentation, classification, dimensionality reduction
- Location: `eaui2026_v2.ipynb`, cells 25+
- Contains: Cross-tabulations, skill classification (`nivel_habilidades`), MCA biplot, boxplots, regression-ready functions
- Depends on: Layer 4 (analysis functions)
- Used by: Visualization and reporting

**Layer 6: Visualization & Output**
- Purpose: Render insights as styled tables, static plots, and interactive dashboards
- Location: `eaui2026_v2.ipynb`, cells 32, 35
- Contains: `generar_grafico()` (matplotlib), `crear_grafico_interactivo()` (Plotly)
- Depends on: Layer 5 (analysis results)
- Used by: End user (HTML export, notebook view)

## Data Flow

### Primary Request Path: Single-Variable Frequency Analysis

1. **User invokes `dstats(df, 'sexo', tipo='frecuencia', factor='fe_personas', estilo=True)`** (`eaui2026_v2.ipynb:cell 20`)
   - Specifies variable name (`sexo`), analysis type (`frecuencia`), weighting (`fe_personas`), and styling
2. **`dstats()` validates columns exist** and extracts weighting column
3. **Groups by variable, sums weights** (`data_df.groupby(var, observed=True)[factor].sum()`)
   - Result: `n_ponderado` (weighted count per category)
4. **Computes percentages** (`n_ponderado / total * 100`)
5. **Orders categories** via `_ordenar()` using `ORDEN_CATEGORIAS['sexo']` lookup
6. **Appends 'Total' row** with sums
7. **Applies `fordf()` styling** (conditional formatting: integers for counts, 1-decimal for %ile, table caption)
8. **Returns** `Styler` object for Jupyter HTML display

### Cross-Tabulation Flow: Multiple Variables

1. **User invokes `dstats(df, 'acceso_internet_hogar', tipo='cruzada', cruce='gse', factor='fe_hogar')`**
2. **`dstats()` pivots data** (`pd.pivot_table(values=factor, index=var, columns=cruce, aggfunc='sum')`)
   - Result: matrix with variable categories as rows, cruce categories as columns
3. **Computes column percentages** (`t.div(t.sum(axis=0), axis=1).mul(100)`)
   - Each column sums to 100% (distributes within cruce group)
4. **Orders rows and columns** via `ORDEN_CATEGORIAS` lookups
5. **Interleaves** `n` and `%` columns for each cruce category
6. **Appends 'Total' row** and applies `fordf()` styling
7. **Returns** combined DataFrame with alternating n-pct columns

### Multiple-Response Analysis Flow

1. **User invokes `analizar_rm('Q8', factor='fe_personas', top_n=10)`** (`eaui2026_v2.ipynb:cell 22`)
2. **Lookup** `GRUPOS_RM['Q8']` → gets 19 columns starting with `Q8_`
3. **Filter valid columns** (columns that exist in df)
4. **Compute base** = weighted sum of rows where any Q8 column is not NaN
5. **For each column:**
   - Count respondents with value 1 (marked yes for this option)
   - Weight sum: `df.loc[df[col]==1, factor].sum()`
   - Percentage: `weighted_sum / base * 100`
6. **Sort by percentage descending**, take top N
7. **Fetch readable labels** via `etiquetas_limpias` dict lookup
8. **Apply `fordf()` styling and return** as Styler

**State Management:**
- **Immutable:** Raw df (never filtered for analysis; weighting only via groupby aggregation)
- **Mutable:** Columns are recoded in-place with text labels (section 7)
- **Shared references:** `ORDEN_CATEGORIAS`, `GRUPOS_RM`, `etiquetas_limpias` are global dicts referenced by all functions
- **Weighting logic:** Functions never hard-code weight column; always passed as `factor` parameter

## Key Abstractions

**`ORDEN_CATEGORIAS` Dictionary:**
- Purpose: Enforces consistent display ordering across all tables and plots
- Examples: `'sexo': ['Hombre','Mujer']`, `'gse': ['AB','C1','C2','C3','D','E']` (high to low)
- Pattern: Categorical variables have fixed orderings; unordered categories not in dict retain their natural order or are appended

**`GRUPOS_RM` Dictionary:**
- Purpose: Groups related multiple-response columns under a single semantic label
- Examples: `'Q8'` maps to 19 digital skill questions; `'P3'` maps to 8 access device types
- Pattern: Key (str) → (description, [column list]) tuple

**`dstats()` Function:**
- Purpose: Unified interface for frequency/crosstab/weighted mean/sum analysis
- Signature: `dstats(data_df, variables, tipo, cruce=None, factor=None, transponer=False, estilo=True)`
- Pattern: Single function handles 4+ analysis patterns via `tipo` parameter; always returns DataFrame or Styler

**Weight Columns (`fe_hogar`, `fe_personas`):**
- Purpose: Adjust sample counts to population totals
- Usage: Pass as `factor` parameter to `dstats()`; never hardcoded in functions
- Correctness: Must match variable scope (household vs. person)

**Text Label Encoding:**
- Purpose: Replace numeric codes with human-readable labels once at section 7, never re-encode
- Pattern: All recodifications in section 7 are in-place (`df[col] = df[col].map(...)`), overwriting numeric columns
- Implication: All downstream analysis assumes text values (no conditional logic on numeric codes)

## Entry Points

**Section 1: Carga (Load)**
- Location: `eaui2026_v2.ipynb`, cell 2
- Triggers: Manual execution of cell
- Responsibilities: Load SPSS file via `pyreadstat.read_sav()`, instantiate `df` and `meta` globals

**Section 2: GSE Derivation**
- Location: `eaui2026_v2.ipynb`, cell 4
- Triggers: Executed after section 1; adds `gse` column to df
- Responsibilities: Compute GSE from education + occupation lookup tables before any renaming

**Section 6: Renombrado**
- Location: `eaui2026_v2.ipynb`, cell 14
- Triggers: Must run after GSE derivation (section 2), before recodifications (section 7)
- Responsibilities: Rename 53 SPSS codes to short names; recodify education, occupation in their new names

**Section 7: Recodificaciones**
- Location: `eaui2026_v2.ipynb`, cell 16
- Triggers: After section 6; establishes text labels for all categorical variables
- Responsibilities: In-place encoding of all numeric to text; must complete before any analysis

**Section 9: Analysis Functions**
- Location: `eaui2026_v2.ipynb`, cell 20
- Triggers: After section 8 (income derivation); makes `dstats()`, `fordf()`, `ORDEN_CATEGORIAS` available
- Responsibilities: Define all analytic primitives

**Section 10: Multiple-Response Groups**
- Location: `eaui2026_v2.ipynb`, cell 22
- Triggers: After section 9; makes `GRUPOS_RM`, `analizar_rm()` available
- Responsibilities: Define grouped response sets and analysis functions

**Section 11+: Analysis**
- Location: `eaui2026_v2.ipynb`, cells 25+
- Triggers: After section 10; all analytic functions available
- Responsibilities: Run exploratory analysis, classification, visualization

## Architectural Constraints

- **Execution Order:** Sections 1–10 are mandatory and sequential. Any cell out of order breaks downstream references.
- **Global State:** All global variables (`df`, `meta`, `ORDEN_CATEGORIAS`, `GRUPOS_RM`, `etiquetas_limpias`) are defined at module scope and mutated in place. No isolation between cells.
- **Circular Imports:** Not applicable (no modules).
- **Immutability Expectations:** 
  - Raw df should not be filtered for analysis (use groupby aggregation instead)
  - Recodifications are one-way (numeric → text); no reverse mapping
  - Weight columns are read-only after loading
- **Data Type Consistency:** After section 7, all categorical columns contain text strings (no numeric codes). Downstream functions assume this invariant.
- **Missing Value Handling:** Section 5 handles `9999999` sentinel; all downstream functions treat `NaN` as "not responded" or "not applicable" and skip in aggregations.

## Anti-Patterns

### Anti-Pattern: Filtering df Without Recomputing Weights

**What happens:** User writes `df_filtered = df[df['gse']=='AB']`, then calls `dstats(df_filtered, 'sexo', factor='fe_hogar')`.

**Why it's wrong:** Weight columns (`fe_hogar`) sum to the full population for the unfiltered sample. A filtered df with un-adjusted weights will produce counts and percentages that don't scale to any meaningful population total (will under-count the filtered group).

**Do this instead:** Use `dstats()` with the full df and specify `cruce='gse'` to show breakdown by GSE. If you truly need to filter, recompute weights: `df_filtered['fe_hogar_adj'] = df_filtered['fe_hogar'] / df_filtered['fe_hogar'].sum() * df['fe_hogar'].sum()` (advanced).

### Anti-Pattern: Reordering Sections 1–10

**What happens:** User moves section 7 (recodifications) before section 6 (renaming). Recodification maps use short names (e.g., `'sexo'`), but section 6 hasn't renamed `Q1_2` yet.

**Why it's wrong:** Will raise `KeyError: 'sexo'` in section 7 recodification.

**Do this instead:** Keep sections 1–10 in fixed order. If you need custom preprocessing, insert it *after* section 10, not before.

### Anti-Pattern: Using Numeric Codes After Section 7

**What happens:** Analysis code checks `if df['sexo'] == 1:` expecting 1 to mean 'Hombre'.

**Why it's wrong:** Section 7 overwrites `sexo` with text ('Hombre'/'Mujer'). Numeric comparison will never match.

**Do this instead:** Always use text labels after section 7: `df['sexo'] == 'Hombre'`.

## Error Handling

**Strategy:** Minimal error handling. Failures occur at cell execution time and halt the notebook.

**Patterns:**
- `dstats()` validates column existence upfront with `ValueError`
- `analizar_rm()` validates group key exists in `GRUPOS_RM` with `ValueError`
- `_ordenar()` silently ignores categories in `ORDEN_CATEGORIAS` that don't exist in data (safe reuse of global ordering dict)
- Missing values (`NaN`) are skipped in `groupby()` and weighted aggregations (pandas default)

## Cross-Cutting Concerns

**Logging:** None. Diagnostic output via `print()` statements in setup sections (e.g., "GSE: {...}" in section 2).

**Validation:** 
- Section 2 prints GSE distribution to confirm derivation
- Section 7 prints sample value counts to confirm recodifications
- Section 18 prints income-by-GSE table to confirm monotonic income increase with GSE

**Authentication:** Not applicable (file-based data, no external API).

---

*Architecture analysis: 2026-04-27*
