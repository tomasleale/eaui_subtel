# External Integrations

**Analysis Date:** 2026-04-27

## APIs & External Services

**None** — Project operates entirely on local file-based data. No external APIs or remote services are used.

## Data Storage

**Databases:**
- None (no SQL/NoSQL database)

**File Storage:**
- Local filesystem only
  - Source data: SPSS `.sav` files in `data/sav/` (authoritative)
  - Secondary formats: CSV in `data/csv/`, Excel in `data/xlsx/`, exported CSV output
  - Working directory: `/Users/tomas/github/eaui_subtel/` (hardcoded in notebooks)

**Data Sources:**
- `data/sav/2026.sav` - Current production dataset (5,000 records, 587 variables) loaded via `pyreadstat.read_sav()` in section 1 (Carga)
- `data/sav/2008.sav`, `2011.sav`, `2012.sav`, ..., `2025.sav` - Historical survey waves (11 files covering 2008–2025)
- `data/xlsx/` - Excel exports (10 files covering main survey years 2012–2025)
- `data/csv/` - CSV versions of survey data (year-by-year files)
- `data/2026_procesado.csv` - Processed output: cleaned and recoded 2026 data after notebook execution

**Caching:**
- None (data loaded fresh into memory each notebook run)

## Data Formats

**Primary Input:**
- SPSS `.sav` (Statistical Package for the Social Sciences)
  - Metadata: column names, labels, value label mappings provided by `pyreadstat`
  - Example: `data/sav/2026.sav` → 5,000 × 587 DataFrame + metadata dict (`meta.column_names`, `meta.column_labels`, `meta.variable_value_labels`)
  - Read function: `pyreadstat.read_sav(filepath)` → `(df, meta)` tuple

**Secondary Input:**
- Excel `.xlsx` files in `data/xlsx/` (optional alternative to `.sav`)
- CSV `.csv` files in `data/csv/` (optional alternative to `.sav`)

**Output:**
- CSV export: `data/2026_procesado.csv` (processed, recoded, weighted data)
- Matplotlib/Seaborn plots: displayed in notebook cells
- Plotly interactive charts: generated in browser within Jupyter
- MCA coordinates: calculated by `prince.MCA.fit()` and used for biplot visualization

## Authentication & Identity

**None** — No authentication required. All data is local. No user accounts or API tokens used.

## Monitoring & Observability

**Error Tracking:**
- None (no external error service)

**Logs:**
- Console output in Jupyter notebook cells only
  - Example: `print(f"Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")` (section 1)
  - Validation: `print(f"Etiquetas procesadas: {len(etiquetas_limpias)}")` (section 3)
  - Weight summaries and distribution checks printed in-cell

**Debugging:**
- Interactive REPL in Jupyter (`df.head()`, `df.info()`, `ORDEN_CATEGORIAS.keys()`)
- Cell-by-cell execution allows inspection of intermediate DataFrames

## CI/CD & Deployment

**Hosting:**
- None (Jupyter notebooks run locally or on JupyterHub instance)

**CI Pipeline:**
- None (no automated tests, linting, or validation pipeline)

**Version Control:**
- Git repository (`.git/` exists), but no hooks or pre-commit checks for notebooks

## File Format Dependencies

**SPSS `.sav` Format:**
- Binary format specific to IBM SPSS Statistics
- Metadata richness: value labels (e.g., `1 → 'Hombre'`, `2 → 'Mujer'`) embedded in file
- Parsed by `pyreadstat` into Python dicts: `meta.column_labels`, `meta.variable_value_labels`
- Critical: GSE derivation (section 2) uses SPSS numeric codes before labels are applied; renaming (section 6) depends on working with numeric codes, then recodification (section 7) applies labels
- Example from `eaui2026_v2.ipynb`:
  ```python
  df, meta = pyreadstat.read_sav("/Users/tomas/GitHub/eaui_subtel/data/sav/2026.sav")
  # Returns: df (5,000 × 587), meta with column_names, column_labels, variable_value_labels
  ```

**Metadata Dictionary:**
- `meta.column_names` — list of variable codes (e.g., `['REGISTRO', 'FECHAFIN', 'COD_REGION', ..., 'Q8_19']`)
- `meta.column_labels` — list of SPSS descriptions (e.g., `['Número de registro', 'Fecha de fin...', 'Región', ...]`)
- `meta.variable_value_labels` — dict of variable codes to {code: label} mappings (e.g., `{'Q1_2': {1: 'Hombre', 2: 'Mujer'}}`)
- Used in sections 3, 4, 6 to build clean variable dictionary (`diccionario`) and label lookups

**CSV Output Format:**
- `data/2026_procesado.csv` — Processed data after all transformations
- Rows: 5,000 (survey respondents)
- Columns: 588 (original 587 + 1 derived `gse` column)
- Text encoding: UTF-8
- Delimiter: comma
- Can be loaded with `pd.read_csv('data/2026_procesado.csv')`

## Weighting & Population Inference

**Weighting Columns:**
- `fe_hogar` (household weight) — Ponderación hogar — used for household-level analysis
- `fe_personas` (person weight) — Ponderación personas — used for individual-level analysis
- `pond_hogar` (normalized household weight) — Alternative; used in some probability models
- `pond_personas` (normalized person weight) — Alternative; used in some probability models
- Calculated by SUBTEL during survey design/post-stratification; stored in raw SPSS file
- All weighted calculations multiply by factor: `df.groupby(...)[factor].sum()` → population-level inference

**Survey Design:**
- Cross-sectional (not longitudinal)
- Representative at national and regional levels
- 5,000 respondents in 2026 wave (minimum observed case count: 1 respondent × weight = population units)
- Weights ensure that analysis results scale to total Chilean internet access population

## Outputs & Exports

**Visualizations:**
- Matplotlib figures: static PNG/PDF in Jupyter output
- Plotly interactive charts: HTML within Jupyter notebook
- MCA biplot (section 11): scatter plot with category coordinates and annotations

**Analysis Tables:**
- `dstats()` output: pandas DataFrame (unweighted) or Styler (styled HTML)
  - Frequency tables, cross-tabulations, weighted means
- `analizar_rm()` output: multiple-response group analysis
- ACM coordinates: DataFrame with row/column points from `prince.MCA`

**No API Exports:**
- Results are not automatically synced to external databases or APIs
- Outputs remain in notebook memory or as static files

## Environment & Path Configuration

**Hardcoded Paths:**
- `/Users/tomas/GitHub/eaui_subtel/data/sav/2026.sav` — Production data source (section 1)
- `/Users/tomas/github/eaui_subtel/` — Working directory (relative to repo root)
- All file paths assume local filesystem access

**No Environment Variables:**
- No `.env` file
- No configuration file for paths, database URLs, or API keys
- Notebook is portable only if data directory structure is replicated

---

*Integration audit: 2026-04-27*
