# Technology Stack

**Analysis Date:** 2026-04-27

## Languages

**Primary:**
- Python 3.8+ (tested with 3.10+) - Data analysis, notebook execution, all analysis logic

**Secondary:**
- None (pure Python project)

## Runtime

**Environment:**
- Jupyter Notebook environment (IPython kernel)
- Python 3.10+ recommended

**Package Manager:**
- pip
- Lockfile: Not present (no `requirements.txt`, `Pipfile`, or `poetry.lock`)

## Frameworks

**Core Analysis:**
- Jupyter Notebook - Interactive data analysis and visualization environment (`eaui2026_v2.ipynb`, `eaui2026.ipynb`)
- pandas - Data manipulation, aggregation, weighted statistics (`dstats()` functions)

**Statistical & Analytical:**
- prince 0.7.0+ - Multiple Correspondence Analysis (MCA) for exploring relationships between categorical variables (section 11, `eaui2026_v2.ipynb`)
- numpy - Numerical computations, array operations, weighting calculations
- seaborn - Statistical data visualization, color palettes
- matplotlib - Low-level plotting and figure customization (biplot generation, `generar_grafico()`)
- plotly - Interactive visualization with Plotly Express (`crear_grafico_interactivo()`)

**Data I/O:**
- pyreadstat - Read SPSS `.sav` files (section 1, Carga: `pyreadstat.read_sav()`)

## Key Dependencies

**Critical:**
- pyreadstat - Reads SPSS .sav source files (5,000 rows × 587 columns from `data/sav/2026.sav`) and provides SPSS metadata (variable labels, value labels)
- pandas - Core data structure (DataFrame), weighted aggregation, cross-tabulation, categorical encoding
- prince - MCA fitting and coordinate extraction for biplot analysis (section 11)
- numpy - Array operations for weighted averaging (`np.average(weights=)`)

**Visualization:**
- matplotlib - Axes-level customization, biplot annotations, grid/spine control
- seaborn - High-level plotting (color palettes, legend formatting)
- plotly - Browser-based interactive charts (Plotly Express API for bar/pie/stacked charts)

## Configuration

**Environment:**
- Virtual environment recommended (instructions in `CLAUDE.md`)
- No `.env` files or configuration management required
- Paths are hardcoded in notebooks (e.g., `/Users/tomas/GitHub/eaui_subtel/data/sav/2026.sav`)

**Build:**
- No build configuration file (no `setup.py`, `pyproject.toml`, or build script)
- Notebooks are directly executable in Jupyter
- Execution order is mandatory: sections 1–10 setup; sections 11+ analysis

## Platform Requirements

**Development:**
- macOS (tested path: `/Users/tomas/...`), but Python 3.8+ runs on Windows, Linux, macOS
- Jupyter installed (`pip install jupyter`)
- 4GB+ RAM recommended (5,000 rows × 587 columns × operations)

**Production:**
- Jupyter server or JupyterHub for notebook execution
- Python 3.8+ runtime
- Network access to data files (`data/sav/`, `data/xlsx/`, `data/csv/`)
- All dependencies in memory during execution (no persistence/caching layer)

## Dependency Installation

```bash
pip install pyreadstat prince pandas numpy seaborn matplotlib plotly jupyter
```

**Verified packages:**
- pyreadstat ≥ 1.1 (SPSS file reader)
- prince ≥ 0.7 (MCA algorithm)
- pandas ≥ 1.0 (data manipulation)
- numpy ≥ 1.18 (numerical compute)
- seaborn ≥ 0.11 (visualization)
- matplotlib ≥ 3.3 (plotting)
- plotly ≥ 6.0 (interactive charts)

---

*Stack analysis: 2026-04-27*
