# Codebase Concerns

**Analysis Date:** 2026-04-27

## Data Quality Issues

### Missing Data Handling Fragility

**What happens:** Section 5 of `eaui2026_v2.ipynb` replaces the sentinel value `9999999` with `NaN` in 17 specific monetary/amount columns only (`P11`, `Q7_4`, `P17_*`, `P19_*`, `Q40_*`, `Q42*`). However, SPSS metadata is not systematically consulted to identify all sentinel-coded variables.

**Files:** `eaui2026_v2.ipynb` (cell 12: NS/NR treatment)

**Impact:** 
- Other columns may contain hidden sentinel codes (999, 99, 9) that are not being replaced with `NaN`, leading to spurious values in descriptive statistics and weighted analysis
- Analyses that assume complete-case deletion may retain invalid sentinel codes as valid data points
- Weighting calculations can be distorted if sentinel values are included in aggregations

**Fix approach:**
1. Systematically inspect SPSS metadata (`meta.variable_value_labels`) to identify all columns with explicit "NS/NR" or "No sabe" codes
2. Build comprehensive mapping of sentinel values per variable type (amount, categorical, frequency)
3. Centralize sentinel replacement logic before section 7 (recodifications)
4. Add validation: check for unexpectedly high frequencies of extreme codes (99, 999, 9999999)

---

### Missing Value Patterns in Weighting Factors

**What happens:** Weighting columns (`fe_hogar`, `fe_personas`, `pond_hogar`, `pond_personas`) are imported as-is from SPSS. No validation checks confirm they sum to expected population totals, contain only positive values, or have no missing values.

**Files:** `eaui2026_v2.ipynb` (cell 1: load), cells using `factor=` parameter in `dstats()`, `analizar_rm()`

**Impact:**
- If any weight row is `NaN` or zero, weighted aggregations silently drop those observations without warning
- Analyses may undercount or overcount population totals without visible error
- Cross-survey comparisons (e.g., comparing 2026 to 2024/2025) will fail if weights have different missing patterns

**Fix approach:**
1. Add validation block after data load:
   - Check `fe_hogar.sum()` ≈ census population for target regions
   - Check `fe_personas.sum()` ≈ census population
   - Verify no negative or zero weights
   - Flag and document any NaN weights
2. Document expected weight totals in CLAUDE.md for reference
3. Raise error if weight sums deviate >5% from expected

---

### Incomplete GSE Derivation

**What happens:** Section 2 derives GSE from `A10` (education) and `A11` (occupation head of household) using a hardcoded lookup table `_M` (cell 4). The matrix maps `(occupation_code, educ_group)` tuples to GSE categories. However, no validation checks if all combinations in the data are present in the matrix.

**Files:** `eaui2026_v2.ipynb` (cell 4: GSE derivation)

**Impact:**
- Unmapped combinations fall through to `np.nan` without warning, silently creating `NaN` in the `gse` column
- These missing GSE values then filter observations out of all downstream analyses
- Current summary shows GSE with no `NaN` visible, but the `.value_counts()` output obscures unknown mapping failures

**Fix approach:**
1. After GSE derivation, validate:
   ```python
   missing_gse = df[df['gse'].isna()]
   if len(missing_gse) > 0:
       combinations = missing_gse[['A10', 'A11']].drop_duplicates()
       print(f"WARNING: {len(missing_gse)} rows with unmapped GSE: {combinations.values.tolist()}")
   ```
2. Add edge cases to `_M` for any observed unmapped combos, or document why they are intentionally excluded
3. Document what % of data is lost due to GSE filtering

---

### Income Band Assumptions Untested

**What happens:** Section 8 derives continuous income (`ingreso_pm`) by taking the midpoint of income ranges that vary by household size. For the highest bracket (`*7`), the formula uses `v[0]*1.5` (1.5× the lower bound) as an estimate because the upper bound is `None`.

**Files:** `eaui2026_v2.ipynb` (cell 18: ingreso_pm derivation)

**Impact:**
- High-income households are systematically underestimated (multiplier `1.5` is arbitrary and untested against actual survey data)
- Income-based analyses (mean by GSE, income comparisons) will have compressed upper tail, affecting measures of income inequality
- Cross-wave comparisons break if the income ceiling bracket changes between survey years (e.g., 2024 vs. 2026)

**Fix approach:**
1. Document the 1.5× assumption and its source (if from SUBTEL guidance) or justify empirically
2. Conduct sensitivity analysis: recalculate analysis with 1.2× and 2.0× multipliers and report how results change
3. Compare mean income by GSE across survey years (2024, 2025, 2026) — if 2026 shows unrealistic upward jump, suspect income ceiling issue
4. For policy analysis, report confidence intervals or flagged results when they depend on upper-bracket assumptions

---

## Assumptions and Fragility

### Mandatory Execution Order is Unforced

**What happens:** CLAUDE.md and cell 0 of the notebook state "Orden de ejecución: Carga → GSE → Etiquetas → NS/NR → Renombrado → Recodificaciones → Funciones". However, Jupyter allows cells to be executed out of order or skipped. If a user runs section 7 (recodificaciones) before section 2 (GSE derivation), the GSE variable will be missing, breaking all analyses.

**Files:** `eaui2026_v2.ipynb` (cells 2–10)

**Impact:**
- Silent data corruption: analyses complete but with wrong GSE values (numeric codes instead of text)
- Difficult to debug in collaborative environments where analysts may not follow documented order
- No error message prompts users to re-execute setup sections
- Production workflows may fail unexpectedly if notebook state is corrupted

**Fix approach:**
1. Add guard cells at the start of analysis sections (e.g., section 11) that check for required objects:
   ```python
   assert 'gse' in df.columns and df['gse'].dtype.name == 'category', "Section 2 (GSE) must be executed first"
   assert 'dstats' in dir(), "Section 9 (Funciones) not loaded. Execute sections 1-9 first"
   ```
2. Refactor into a single `.py` module (`eaui_setup.py`) with functions for each setup step, importable from the notebook
3. Add a validation cell that must be run after any analysis section to confirm data state

---

### Variable Recodification is In-Place and Lossy

**What happens:** Section 7 overwrites numeric columns with text labels directly, without creating `_rec` or `_label` suffixed versions. Once recodified, the original numeric codes are permanently lost from the DataFrame, and there is no way to recover them for debugging or alternative coding schemes.

**Files:** `eaui2026_v2.ipynb` (cells 16–24: recodifications)

**Impact:**
- If a recode mapping contains an error (e.g., a missed code or typo in a label), the error propagates to all downstream analyses with no way to revert
- Exploratory recoding (e.g., testing alternative income group boundaries) requires re-running the entire notebook from cell 1
- Comparison with SPSS output becomes impossible without re-loading the raw `.sav` file

**Fix approach:**
1. Preserve original columns by renaming before recodification:
   ```python
   df['sexo_orig'] = df['sexo']  # Keep original before map()
   df['sexo'] = df['sexo'].map({1: 'Hombre', 2: 'Mujer'})
   ```
2. Document which columns have preserved originals and update CLAUDE.md with recovery instructions
3. Create a recodification validation function that logs mappings and identifies unmapped values

---

### Weighting Factor Selection is Manual and Error-Prone

**What happens:** All `dstats()` and `analizar_rm()` calls require explicit `factor=` specification. The default for `dstats()` is `None` (which raises an error), but `analizar_rm()` defaults to `'fe_hogar'`. This inconsistency requires analysts to remember which factor applies to each variable.

**Files:** `eaui2026_v2.ipynb` (cells 20, 22: function signatures)

**Impact:**
- Individual-level analyses (e.g., `sexo`, `edad`) incorrectly analyzed with `fe_hogar` if user forgets to override
- Results appear plausible but are silently wrong: proportions will not match the actual population distribution
- No warning or error when wrong factor is applied
- CLAUDE.md guidance is text-based and easy to overlook

**Fix approach:**
1. Infer correct factor from variable metadata:
   - Create a dict mapping variable names to their appropriate factor:
     ```python
     VARIABLE_FACTOR_MAP = {
         'sexo': 'fe_personas', 'edad': 'fe_personas',
         'acceso_internet_hogar': 'fe_hogar', 'ingreso_hogar': 'fe_hogar',
         ...
     }
     ```
   - Modify `dstats()` to auto-select factor if not provided:
     ```python
     if factor is None:
         factor = VARIABLE_FACTOR_MAP.get(variables[0], 'fe_personas')
         print(f"Auto-selected factor={factor}")
     ```
2. Add runtime warning if a variable is analyzed with the wrong factor
3. Document the mapping in CLAUDE.md with a reference table

---

## Data Scope and Interpretation Risks

### Cross-Wave Comparisons Lack Harmonization

**What happens:** The codebase loads 11 SPSS files from different survey years (2008, 2011–2018, 2024–2026) but the current notebook focuses exclusively on 2026. Variable codes, categories, and mappings differ between waves (e.g., education categories expanded in 2024 vs. 2018).

**Files:** `data/sav/` contains 11 `.sav` files; only `2026.sav` is loaded in `eaui2026_v2.ipynb`

**Impact:**
- Any attempt to merge or compare 2026 data with prior waves will fail or produce misleading results due to unmapped categories
- The recodification mapping in section 5 is 2026-specific; applying it to 2018 data would map wrong codes to labels
- Policy analysis across time cannot be published without major data cleaning effort

**Fix approach:**
1. Create a metadata file documenting code changes per survey year (e.g., `code_mapping_by_wave.csv`)
2. Build a unified recodification function that accepts both variable name and survey year:
   ```python
   recode_value(col_name, raw_value, survey_year=2026) -> label
   ```
3. Add a cross-wave validation step to identify structural breaks in variable definitions
4. Document in CLAUDE.md which analyses are 2026-specific vs. compatible with other waves

---

### Incomplete Case Handling in MCA

**What happens:** Section 11 applies MCA (multiple correspondence analysis) on `df_acm`, which is filtered to complete cases (`dropna()`). This reduces the effective sample from 5,000 to ~4,750 rows (from `mask_q8` filter) then further to ~4,200 rows (from complete-case drop). No documentation explains which observations are excluded or why.

**Files:** `eaui2026_v2.ipynb` (cell 30: ACM analysis)

**Impact:**
- MCA results represent a non-random subset of the survey: dropouts are likely non-random (e.g., respondents with missing education are poorer, older, more rural)
- Inferences about population structure from MCA biplot are biased toward complete responders
- No weighting is applied in MCA, so high-response-burden groups (wealthy, educated) are overrepresented
- Report readers may not realize inferences apply only to ~84% of the sample

**Fix approach:**
1. Document the flow of sample reduction:
   ```python
   print(f"Initial: {len(df)} rows")
   print(f"After Q8 filter: {mask_q8.sum()} rows ({mask_q8.sum()/len(df)*100:.1f}%)")
   print(f"After dropna: {len(df_acm)} rows ({len(df_acm)/mask_q8.sum()*100:.1f}%)")
   ```
2. Perform sensitivity analysis: run MCA on imputed or weighted data and compare results
3. Add caution to CLAUDE.md: "MCA results apply to complete cases only; interpret as exploratory"
4. Consider using multiple imputation or inverse-probability weighting for MCA

---

## Security & Privacy Concerns

### Personal Data Stored in Output CSV

**What happens:** Cell 27 of deprecated `eaui2026.ipynb` exports the full processed DataFrame to `data/2026_procesado.csv`, which includes `fecha_fin` (interview end date) and `comuna` (municipality code). These quasi-identifiers combined with demographic data (sexo, edad, gse, region) could enable re-identification of individuals, especially in small municipalities.

**Files:** `eaui2026.ipynb` (cell 28: export), `data/2026_procesado.csv` (output file)

**Impact:**
- CSV file may be accessible to unauthorized users if repo is cloned or shared
- Combined with external data (e.g., municipal voter registry by age and education), quasi-identifiers could enable re-identification
- Risk is heightened in 2024–2026 data where sample is smaller and more recent (survey participants may still be identifiable by colleagues)
- Legal/compliance issue: SUBTEL survey may have privacy terms forbidding public export

**Fix approach:**
1. Remove or hash sensitive quasi-identifiers before export:
   ```python
   df_export = df.drop(columns=['fecha_fin', 'comuna', 'REGISTRO'])  # Remove date and location
   df_export['edad_grupo'] = pd.cut(df['edad'], bins=[0, 20, 40, 60, 100])  # Coarsen age
   df_export.to_csv(...)
   ```
2. Add a note in CLAUDE.md: "Do not share unprocessed 2026_procesado.csv with external parties. If exporting for publication, remove/coarsen quasi-identifiers."
3. Update `.gitignore` to prevent accidental commit of unprocessed export:
   ```
   data/2026_procesado.csv
   data/20*_procesado.csv
   ```

---

### Metadata Assumes Public Access

**What happens:** `etiquetas_limpias` dictionary (section 3) retains all SPSS variable labels, which may contain survey-instrument metadata, skip patterns, or clarifications that reveal internal design details or hint at sensitive topics.

**Files:** `eaui2026_v2.ipynb` (cell 6: etiquetas_limpias), function `limpiar_etiqueta()`

**Impact:**
- If code is shared or published, labels may reveal sensitive survey instrument design (e.g., "Aymara [A12.- ¿Algún miembro...")
- While labels are already in SPSS metadata (semi-public), including them in Python code makes them more discoverable
- Not a direct security risk, but increases surface area for inference attacks

**Fix approach:**
1. Keep etiquetas_limpias for internal use only; do not export to shared CSV or API
2. Document in CLAUDE.md: "etiquetas_limpias is internal metadata. Do not share with non-researchers."
3. If publishing analysis code, replace full labels with generic descriptions

---

## Dependency Brittleness

### Hardcoded File Paths

**What happens:** Cell 2 of `eaui2026_v2.ipynb` hardcodes:
```python
df, meta = pyreadstat.read_sav("/Users/tomas/GitHub/eaui_subtel/data/sav/2026.sav")
```
and cell 28 of `eaui2026.ipynb` exports to:
```python
df.to_csv("/Users/tomas/GitHub/eaui_subtel/data/2026_procesado.csv", ...)
```

**Files:** `eaui2026_v2.ipynb` (cell 2), `eaui2026.ipynb` (cell 28)

**Impact:**
- Notebook will fail if moved to different machine or if repo is cloned to non-standard path
- "GitHub" in path is misspelled (should be lowercase "github" on case-sensitive filesystems)
- Other users cannot run the notebook without editing hardcoded paths
- CI/CD automation impossible without path modification

**Fix approach:**
1. Replace hardcoded paths with relative paths:
   ```python
   import os
   sav_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sav', '2026.sav')
   df, meta = pyreadstat.read_sav(sav_path)
   ```
   OR use `pathlib`:
   ```python
   from pathlib import Path
   sav_path = Path(__file__).parent.parent / 'data' / 'sav' / '2026.sav'
   ```
2. If Jupyter, compute relative to notebook location:
   ```python
   import os
   notebook_dir = os.path.dirname(os.path.abspath(__file__))  # Fails in Jupyter, use os.getcwd()
   sav_path = os.path.join(os.getcwd(), '..', 'data', 'sav', '2026.sav')
   ```
3. Document in CLAUDE.md: "Run notebook from the repo root directory"

---

### Prince (MCA) Package Version Unspecified

**What happens:** Cell 1 imports `prince` for MCA but there is no `requirements.txt`, `environment.yml`, or `setup.py` specifying version. CLAUDE.md mentions installing dependencies but does not pin versions.

**Files:** `eaui2026_v2.ipynb` (cell 1: import prince), CLAUDE.md (setup section)

**Impact:**
- Different versions of `prince` may have different default parameters, coordinate scaling, or randomization behavior, breaking reproducibility
- MCA output (biplot, inertia values) will differ across runs with different `prince` versions
- If `prince` has API-breaking changes, notebook will fail without warning

**Fix approach:**
1. Create `requirements.txt`:
   ```
   pyreadstat==1.2.1
   pandas==2.0.3
   numpy==1.24.3
   seaborn==0.12.2
   matplotlib==3.7.2
   plotly==5.14.1
   prince==0.15.0
   jupyter==1.0.0
   ```
2. Update CLAUDE.md with installation command:
   ```bash
   pip install -r requirements.txt
   ```
3. Document randomness: "Set `random_state=42` in prince.MCA() for reproducibility"

---

### Deprecated Notebook Not Removed

**What happens:** `eaui2026.ipynb` is marked in CLAUDE.md as "Archived draft. Reference only if investigating historical decisions; do not use for active analysis." However, the file remains in the repo, confusing new users.

**Files:** `eaui2026.ipynb` (exists but deprecated)

**Impact:**
- New analysts may accidentally run the deprecated notebook instead of `eaui2026_v2.ipynb`
- Code drifts: if deprecated notebook has stale examples (e.g., old recodification logic), analysts may copy outdated patterns
- Maintenance burden: two nearly-identical notebooks must be kept in sync or documentation updated every time one changes

**Fix approach:**
1. Move to `archived/`:
   ```bash
   mkdir archived/
   mv eaui2026.ipynb archived/
   ```
2. Update `.gitignore` to discourage accidental commits:
   ```
   archived/*.ipynb
   ```
3. Update CLAUDE.md: "Historical notebooks are in `archived/` — do not use for active work"
4. Consider deleting entirely if no ongoing reference need

---

## Testing & Validation Gaps

### No Unit Tests for Recodification Mappings

**What happens:** Sections 5–7 contain ~40 `.map()` calls with hardcoded dictionaries (e.g., `mapa_educ`, `mapa_region`). There are no automated checks to ensure:
- All input codes are mapped (no missing keys)
- No duplicate or conflicting mappings
- Labels match SPSS metadata

**Files:** `eaui2026_v2.ipynb` (cells 16–24)

**Impact:**
- Silent mapping failures: codes not in the dict are replaced with `NaN` without warning
- Typos in labels propagate to all analyses (e.g., "Metropolitana" vs "Metropolitana " with trailing space)
- If SPSS metadata is updated, the hardcoded mappings become out-of-sync

**Fix approach:**
1. Create a test function to validate mappings:
   ```python
   def validate_mapping(df_col, mapping_dict, col_name):
       unmapped = df_col.dropna().unique()
       unmapped = set(unmapped) - set(mapping_dict.keys())
       if unmapped:
           raise ValueError(f"{col_name} has unmapped codes: {unmapped}")
   ```
2. Apply before each recodification:
   ```python
   validate_mapping(df['sexo'], {1: 'Hombre', 2: 'Mujer'}, 'sexo')
   df['sexo'] = df['sexo'].map({1: 'Hombre', 2: 'Mujer'})
   ```
3. Write mappings to a CSV reference table and load dynamically:
   ```python
   mappings = pd.read_csv('mappings.csv')  # columns: column, code, label
   ```

---

### No Output Validation or Sanity Checks

**What happens:** Analysis functions (`dstats()`, `analizar_rm()`) return tables without validating that results are reasonable:
- Percentages sum to 100% (or close to it) after rounding
- No negative percentages or counts
- Weighted counts match expected population totals

**Files:** `eaui2026_v2.ipynb` (cells 20, 22: function definitions)

**Impact:**
- Silently incorrect results (e.g., if a weight is negative or has NaN, the result will be wrong but the function will not error)
- Output tables may have percentages summing to 95% or 105% due to rounding errors or missing data, but no warning is raised
- Analysts must manually inspect each table to catch errors

**Fix approach:**
1. Add validation to `dstats()`:
   ```python
   # After computing percentages
   pct_sum = resultado['porcentaje'].sum()
   if abs(pct_sum - 100) > 0.5:  # Allow 0.5% tolerance
       print(f"WARNING: Percentages sum to {pct_sum:.1f}% (expected 100%)")
   ```
2. Add validation to `analizar_rm()`:
   ```python
   if base_pond <= 0:
       raise ValueError(f"Base pond <= 0 for group {grupo}: {base_pond}")
   ```
3. Document expected behavior: "Percentages may not sum to exactly 100% due to rounding. Deviations >1% indicate a data issue."

---

## Performance Bottlenecks

### MCA is Compute-Heavy Without Progress Reporting

**What happens:** Cell 30 runs `prince.MCA(n_components=2, n_iter=10, random_state=42)` on ~4,200 rows. The operation runs synchronously with no progress bar or timing information, and if it hangs, there is no way to see where it's stuck.

**Files:** `eaui2026_v2.ipynb` (cell 30)

**Impact:**
- On slower machines, MCA may run for 5–10+ minutes with no feedback
- If kernel crashes, user must re-run the entire section without knowing how long to wait
- Hard to debug convergence issues if n_iter needs adjustment

**Fix approach:**
1. Add timing and progress reporting:
   ```python
   import time
   start = time.time()
   mca = prince.MCA(n_components=2, n_iter=10, random_state=42)
   mca.fit(df_acm)
   elapsed = time.time() - start
   print(f"MCA completed in {elapsed:.1f}s")
   ```
2. Document expected runtime: "MCA typically runs in 30–60 seconds on modern hardware. If >2 min, consider reducing n_iter."
3. Consider caching results:
   ```python
   mca_cache = 'mca_fit.pkl'
   if os.path.exists(mca_cache):
       mca = joblib.load(mca_cache)
   else:
       mca = prince.MCA(...).fit(df_acm)
       joblib.dump(mca, mca_cache)
   ```

---

### Plotting Functions Create Large Matplotlib Objects

**What happens:** `generar_grafico()` (cell 32) and ACM biplot (cell 30) create full-sized matplotlib figures that are stored in memory without being explicitly closed. In a long-running notebook session, this accumulates memory.

**Files:** `eaui2026_v2.ipynb` (cells 30, 32)

**Impact:**
- Memory usage grows with each plot call
- Notebook may become sluggish or crash if many plots are generated in sequence
- Closing figures is not enforced, so careless use leaks memory

**Fix approach:**
1. Add `plt.close()` after each plot:
   ```python
   plt.show()
   plt.close('all')  # Explicitly release memory
   ```
2. Return figure objects so users can control lifespan:
   ```python
   def generar_grafico(...):
       fig, ax = plt.subplots(...)
       # ... plotting code ...
       plt.tight_layout()
       return fig, ax
   
   # User controls when to show/close:
   fig, ax = generar_grafico(...)
   fig.show()
   fig.close()
   ```
3. Document: "Call `plt.close('all')` after viewing plots to free memory."

---

## Known Limitations to Document

### Sample Size Interpretation

**Current state:** The 2026 survey has n=5,000 respondents and ~4,850 household weight records. When analyzing by region, smallest groups (Aysén, Arica y Parinacota, Magallanes, Tarapacá) have only 120–150 respondents each.

**Impact:** Subgroup analyses (e.g., MCA biplot by region for Aysén) have very high standard errors; any inference is provisional.

**Mitigation:** Document in captions that estimates for regions with <200 respondents should be interpreted with caution.

---

### Text Label Collisions in Income Ranges

**Current state:** Income band labels in section 8 use currency notation (e.g., "$384 mil") which may not display correctly in non-Spanish locales or if currency symbols are stripped during export.

**Impact:** Exported CSV or tables may show garbled labels in other systems.

**Mitigation:** Use numeric codes for export (e.g., `'ingreso_group_1'`, `'ingreso_group_2'`) and supply a mapping table separately.

---

### No Confidence Intervals or Sampling Variability

**Current state:** All `dstats()` and `analizar_rm()` results are point estimates (weighted proportions) with no confidence intervals, standard errors, or design effects reported.

**Impact:** Analysis appears overly precise. Readers may not understand the sampling variation around estimates.

**Mitigation:** Add standard error calculations:
```python
def dstats(...):
    # Compute SE using design effect from SUBTEL documentation
    # Return DataFrame with columns: 'porcentaje', 'se', 'ci_lower', 'ci_upper'
```

---

## Refactoring Priority

| Concern | Severity | Effort | Priority |
|---------|----------|--------|----------|
| Sentinel value replacement incomplete | High | Medium | 1 |
| Mandatory execution order unforced | High | Low | 2 |
| Hardcoded file paths | Medium | Low | 3 |
| GSE derivation validation missing | Medium | Medium | 4 |
| Weighting factor selection error-prone | Medium | Medium | 5 |
| Deprecated notebook not removed | Low | Low | 6 |
| MCA complete-case handling undocumented | Medium | Low | 7 |
| Recodification mapping tests missing | Medium | Medium | 8 |
| Privacy quasi-identifier risk | Medium | Medium | 9 |
| Prince version unspecified | Low | Low | 10 |

---

*Concerns audit: 2026-04-27*
