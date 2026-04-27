# Testing Patterns

**Analysis Date:** 2026-04-27

## Overview

This is a Jupyter notebook data analysis project. **There are no automated unit tests, integration tests, or test runners.** Quality is ensured through:

1. **Execution order dependencies** — Cells must run sequentially; out-of-order execution fails visibly
2. **Inline data validation** — Print statements and `.value_counts()` confirm transformations
3. **Manual spot-checks** — Analyst reviews printed output after each major section
4. **End-to-end verification** — Full notebook execution validates the complete pipeline

## Test Framework

**Runner:** None — Jupyter kernel executes cells sequentially

**Assertion Library:** None — Use of `print()`, `.value_counts()`, and manual inspection

**Run Commands:**
```bash
jupyter notebook eaui2026_v2.ipynb
```

**Execution Flow:**
1. Open `eaui2026_v2.ipynb` in Jupyter
2. Execute cells 1–10 sequentially (no skip allowed)
3. Execute analysis cells 11+ to verify functions work

## Test File Organization

**Location:** No separate test files — validation embedded in notebook cells

**Naming:** Not applicable

**Structure:** Tests embedded in markdown sections and output cells:

```
Markdown cell: "## 5. Tratamiento NS/NR"
Code cell: Replace sentinel values with NaN
Output cell: Confirmation message "NS/NR reemplazados por NaN."
```

## Test Structure

**Suite Organization:**

Each section (1–10) is a "test suite" validating a stage of data processing:

```
Section 1: Carga (Load)
├─ Load SPSS file → df (5000 rows × 587 cols)
├─ Output: Print row/column counts
└─ Validation: Human reads counts

Section 2: GSE derivado (Derive)
├─ Calculate gse from education + occupation
├─ Output: Print gse distribution by category
└─ Validation: Distribution sums to N=5000

Section 5: NS/NR (Sentinel Handling)
├─ Replace 9999999 with NaN in 18 columns
├─ Output: Confirmation message
└─ Validation: Implicit — no errors raised

Section 7: Recodificaciones (Recode)
├─ Map numeric codes to text labels
├─ Output: Print sexo and acceso distributions
└─ Validation: Distributions show expected categories

Section 8: Ingreso del hogar (Income Derivation)
├─ Calculate income point-estimates from bands
├─ Output: Cross-tabulation of income by GSE
└─ Validation: Income increases monotonically E→AB
```

**Patterns:**

### 1. Assertion Pattern: `.value_counts()` + `.reindex()`

```python
# Section 2 — GSE validation
print('GSE:', df['gse'].value_counts().reindex(_ORDEN_GSE).to_dict())
# Output: GSE: {'AB': 342, 'C1': 533, 'C2': 988, 'C3': 1316, 'D': 833, 'E': 988}
# → Sums to 5000 ✓
```

**Why:** Confirms all cases assigned a category (no NaN); order correct; count matches sample size.

### 2. Coherence Validation: Cross-tabulation

```python
# Section 8 — Income validity check
df.groupby('gse', observed=True)['ingreso_pm'].agg(N='count', Promedio='mean').reindex(_ORDEN_GSE)
#       N  Promedio
# AB   286  2097505
# C1   444  1389884
# C2   826   986176
# C3  1112   799533
# D    704   650022
# E    846   539833
# → Income strictly increases E→AB ✓
```

**Why:** Validates that derived income respects socioeconomic hierarchy (economic validity check).

### 3. Completeness Validation: Mask + Count

```python
# Section 11 — Q8 digital skills respondents
mask_q8 = df[_cols_q8].notna().any(axis=1)  # Has any Q8 response?
base_q8 = int(mask_q8.sum())
print(f"respondentes Q8: {base_q8:,}")
# Output: respondentes Q8: 4,758
# → 4758/5000 (95.2%) responded to Q8 ✓
```

**Why:** Confirms sampling for dependent variables; identifies complete-case requirements.

### 4. Transformation Confirmation: Before/After

```python
# Section 6 — Rename check
print(f"Renombradas: {len(nombres_cortos)} | Columnas totales: {df.shape[1]}")
# Output: Renombradas: 53 | Columnas totales: 588
# → 53 renamed; still 587 original + derived columns ✓
```

**Why:** Verifies column renaming didn't drop or duplicate columns.

### 5. Function Output Validation: Type Check

```python
# Section 9 — dstats type validation
res = dstats(df, 'sexo', tipo='frecuencia', factor='fe_personas', estilo=False)
# res is a DataFrame with columns: ['n_ponderado', 'porcentaje']
# Check: porcentaje sums to ~100
assert res['porcentaje'].sum() > 99, "Percentages don't sum to 100"
```

**Where it happens:** Not explicitly in notebook, but callers verify output shape.

## Mocking

**Framework:** None — Data analysis uses real data

**Patterns:** Not applicable

**What to Mock:** N/A — All functions operate on real DataFrame `df`

**What NOT to Mock:** N/A

## Fixtures and Factories

**Test Data:**

Stored in `data/sav/2026.sav` (5,000 SPSS-format records).

**Location:**
- Source: `/Users/tomas/github/eaui_subtel/data/sav/2026.sav` — Authoritative SPSS file
- Processed: `/Users/tomas/github/eaui_subtel/data/2026_procesado.csv` — Processed output
- Metadata: `/Users/tomas/github/eaui_subtel/diccionario_variables.csv` — 587 variable descriptions

**Fixture Pattern:**

Data loaded once in section 1:
```python
df, meta = pyreadstat.read_sav("/Users/tomas/GitHub/eaui_subtel/data/sav/2026.sav")
# df: 5,000 rows × 587 columns (numeric codes from SPSS)
# meta: SPSS metadata (column labels, value labels, weights)
```

Then modified through sections 2–8. No explicit test fixtures; the notebook itself IS the fixture setup.

## Coverage

**Requirements:** Not enforced; no test coverage metrics configured

**View Coverage:** Not applicable — no test runner

**Implicit Coverage:**

Sections 1–10 must execute without error before analysis:
- Section 1: Load test (file I/O, data integrity)
- Sections 2–8: Transformation tests (derived variables, recodings, weighting)
- Sections 9–10: Function definition tests (functions importable, callable with correct signatures)

Analysis sections 11+ implicitly test whether core functions work:
- `dstats()` called in >50 cells → exercise all branches
- `analizar_rm()` called for 25+ groups → tests multiple-response logic
- `generar_grafico()` called with different parameters → tests plotting pipeline

**Fragile Areas Not Tested:**
- Alternative data formats (CSV, Excel) — only SPSS tested
- Missing weight columns (`fe_hogar`, `fe_personas`) — assumed always present
- Malformed SPSS metadata (out-of-order labels) — no defensive parsing

## Test Types

**Unit Tests:** None formal, but achieved via function-level validation

Example: `dstats()` validation
```python
# Test 1: Frequency table
res = dstats(df, 'sexo', tipo='frecuencia', factor='fe_personas', estilo=False)
assert res['porcentaje'].sum() < 100.1, "Rounding error"
assert len(res) == 3, "Should have 2 values + 1 Total row"  # Not in code, but intention

# Test 2: Cross-tabulation
res = dstats(df, 'acceso_internet_hogar', tipo='cruzada', cruce='gse', factor='fe_hogar', estilo=False)
assert 'AB' in res.index, "Missing gse category"  # Implicit

# Test 3: Weighted average
res = dstats(df, 'edad', tipo='promedio', cruce='gse', factor='fe_personas', estilo=False)
assert res.loc['AB', 'promedio_ponderado'] > 0, "Negative age"  # Implicit
```

**Integration Tests:** Entire notebook execution (sections 1–10)

```bash
# Implicit test: Does the notebook run end-to-end without errors?
jupyter notebook eaui2026_v2.ipynb
# Execute cells 1–10 → No exceptions raised ✓
```

**E2E Tests:** Not formally defined, but section 11+ analysis cells validate the pipeline

```python
# Section 11: Classification test
df['nivel_habilidades'] = df.apply(_nivel, axis=1)
# E-to-E test: 
# - Q8 columns loaded (section 1) ✓
# - Q8 columns exist after rename (section 6) ✓
# - _nivel function defined (section 11) ✓
# - Classification produces 4 categories (Avanzado/Intermedio/Básico/Sin habilidades) ✓
```

## Common Patterns

**Validation After Transformation:**

After each major transformation, a `.value_counts()` or summary statistic confirms correctness:

```python
# After recodification
df['sexo'] = df['sexo'].map({1:'Hombre', 2:'Mujer'})
print(f"sexo: {df['sexo'].value_counts().to_dict()}")  # ← Validation
# Output: sexo: {'Mujer': 2815, 'Hombre': 2185}
```

**Weighted Aggregation Validation:**

Analysis functions use weighting; validation ensures weights are applied correctly:

```python
def dstats(...):
    tot = data_df[factor].sum()  # Total population weight
    res = data_df.groupby(var, observed=True)[factor].sum()  # Group weights
    res['porcentaje'] = (res[factor] / tot * 100)
    # Implicit test: res['porcentaje'].sum() ≈ 100 (or close due to rounding)
```

**Mask-Based Filtering Validation:**

For dependent variables, test confirms respondent subset:

```python
# Multiple-response group analysis
base = df.loc[df[cols].notna().any(axis=1), factor].sum()
# Implicit test: base > 0 (at least one respondent)
# Implicit test: base <= total df weight (no overflow)
```

## Data Validation & Integrity Checks

**Sentinel Value Handling** (`data/sav/2026.sav` → section 5):

18 columns use `9999999` to encode "No sabe/No responde" (NS/NR). Section 5 replaces with NaN:

```python
cols_nsnr = ['P11', 'Q7_4', 'P17_1', 'P17_2', ...]
for col in cols_nsnr:
    if col in df.columns: 
        df[col] = df[col].replace(9999999, np.nan)
print('NS/NR reemplazados por NaN.')
```

**Why:** Prevents `9999999` from being treated as a valid value in analyses. Implicit validation: no ValueError raised when replacing.

**Missing Data Pattern Validation:**

```python
# Section 8 — Income derivation
_rangos = {11:(0,129000), 12:(130000,226000), ...}  # Household-size-specific bands
_mapa_pm = {float(k): ... for k, v in _rangos.items()}
df['ingreso_pm'] = df['ingreso_hogar'].map(_mapa_pm)
# Implicit test: All income_hogar codes map to a valid band
# Risk: If ingreso_hogar contains unknown codes, df['ingreso_pm'] will have NaN
```

**Categorical Validation** (section 7):

```python
df['region'] = df['region'].map({
    1:'Tarapacá', 2:'Antofagasta', ..., 16:'Ñuble'
})
# Implicit test: All region codes 1–16 accounted for
# Risk: If region contains codes > 16, those become NaN
```

**Weight Validation:**

Weights assumed present and positive:

```python
# No validation in code, but implicit requirement:
# - df['fe_hogar'] must exist (section 1 from SPSS)
# - df['fe_hogar'] > 0 for all rows
# - df['fe_personas'] must exist and > 0

# If weights missing or negative → dstats() will fail with KeyError or incorrect results
```

## Reproducibility & Execution Order Dependencies

**Critical Dependency Chain** (sections 1–10):

1. **Section 1** (Carga) — Load `data/sav/2026.sav`
   - Provides: `df`, `meta`
   - Dependency: None
   - Failure: File not found → NameError in section 2

2. **Section 2** (GSE derivado) — Derive `gse` from `A10` + `A11`
   - Provides: `df['gse']`
   - Dependency: `df` from section 1; `A10`, `A11` must not be renamed yet
   - Failure: Skip → `gse` not in df, breaks section 11 MCA
   - Failure: Run after section 6 → `A10`, `A11` already renamed, mapping fails

3. **Section 3** (Etiquetas limpias) — Build `etiquetas_limpias` dict
   - Provides: `etiquetas_limpias`
   - Dependency: `meta` from section 1
   - Failure: Skip → `analizar_rm()` uses bare column codes instead of descriptions

4. **Section 5** (NS/NR) — Replace `9999999` with NaN
   - Provides: Clean monetary columns
   - Dependency: `df` from section 1
   - Failure: Skip → Income analyses include sentinel values, skew results upward

5. **Section 6** (Renombrado) — Rename 53 columns
   - Provides: Short names (`sexo`, `region`, `acceso_internet_hogar`, etc.)
   - Dependency: `df` from section 1; section 2 (GSE) must be complete
   - Failure: Skip → Subsequent sections reference columns that don't exist

6. **Section 7** (Recodificaciones) — Map numeric codes to text labels
   - Provides: Text-labeled columns
   - Dependency: Section 6 (renamed columns)
   - Failure: Skip → Analyses use numeric codes, tables unreadable

7. **Section 8** (Ingreso del hogar) — Derive income variables
   - Provides: `ingreso_pm`, `ingreso_tramo`, `ingreso_grupo`
   - Dependency: Section 6
   - Failure: Skip → Income analyses unavailable

8. **Section 9** (Funciones de análisis) — Define `ORDEN_CATEGORIAS`, `fordf()`, `dstats()`
   - Provides: Core analysis machinery
   - Dependency: Sections 6–7 (for `ORDEN_CATEGORIAS` to reference recoded columns)
   - Failure: Skip → NameError when calling `dstats()` in section 11

9. **Section 10** (Grupos RM) — Define `GRUPOS_RM`, `analizar_rm()`, `analizar_rm_cruce()`
   - Provides: Multiple-response analysis functions
   - Dependency: `df` columns from sections 1, 6
   - Failure: Skip → NameError when calling `analizar_rm()` in section 11

10. **Sections 11+** (Análisis) — Depends on all of 1–10
    - Cannot execute before sections 1–10
    - Each analysis cell implicitly tests all upstream transformations

**Test Execution Order:**

```
✓ Section 1   → df loads
├─ ✓ Section 2 → gse derived (uses A10, A11 numeric)
├─ ✓ Section 5 → Sentinels replaced
├─ ✓ Section 6 → Renamed (educ_jh, ocupacion_jh, region, etc.)
├─ ✓ Section 7 → Recodified (educ_jh, ocupacion_jh now text)
├─ ✓ Section 8 → Income derived
├─ ✓ Section 9 → Functions defined
├─ ✓ Section 10 → MR groups defined
└─ ✓ Section 11+ → Analysis runs end-to-end
```

**Execution Order Violations:**

- **Skip section 2** → `gse` undefined → Section 11 MCA fails with KeyError
- **Skip section 5** → Sentinel `9999999` treated as a valid income → Income stats incorrect
- **Run section 6 before section 2** → `A10`, `A11` renamed before GSE calculated → GSE mapping fails
- **Skip section 9** → `dstats` undefined → Section 11 calls fail with NameError
- **Reorder section 7 & 8** → Works if gse is already defined, but violates documented order

**Manual Verification Checklist** (notebook startup):

Before running analysis (section 11+):

```python
# Quick validation that sections 1–10 executed:
help(dstats)  # → Should show docstring, not NameError
ORDEN_CATEGORIAS.keys()  # → Should show all categorical vars
len(GRUPOS_RM)  # → Should be 25
df['gse'].value_counts()  # → Should show 6 GSE categories
df['nivel_habilidades'].value_counts()  # → Only if section 11 run
```

---

*Testing analysis: 2026-04-27*
