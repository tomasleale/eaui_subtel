# EAUI Subtel Knowledge Graph Report

**Generated:** 2026-05-02  
**Corpus:** CLAUDE.md + informe_final.pdf (partial)  
**Size:** 2 files, ~539 words  
**Extraction:** Semantic analysis (no code AST, notebooks not detected in default patterns)

---

## Executive Summary

This project is a **data processing pipeline for EAUI 2026 survey analysis** — a telecommunications survey conducted by SUBTEL. The core work flows through a single Jupyter notebook (`eaui2026_v3.ipynb`) that loads raw survey data in SPSS format, recodes variables, derives socioeconomic status, and outputs a final report.

**Key observation:** The project is notebook-centric with minimal code/tooling beyond pandas and pyreadstat. No complex architectures detected. The graph is small because the codebase documentation is intentionally compact — most logic lives inside notebook cells.

---

## Nodes by Type

### **Concepts** (Survey Domain, Data Sources)
- **EAUI 2026 Survey** — Main dataset: Encuesta de Acceso y Uso de Internet (Internet Access & Use Survey)
- **SPSS Format (.sav)** — Statistical Package for Social Sciences binary format used for raw data
- **/data/sav/** — Directory holding 19 years of survey data (2008–2026)

### **Tools** (Python Libraries)
- **pyreadstat** — Reads SPSS .sav files into pandas DataFrames
- **pandas** — Core data manipulation library
- **Jupyter** — Interactive notebook environment where all work occurs

### **Methods** (Processing Steps)
- **GSE Derivation** — Calculates socioeconomic status groups from education + occupation (core survey logic)
- **Variable Recoding** — General variable transformation and cleaning
- **Text Normalization** — Applies `re` + `unicodedata` to clean text fields

### **Documents** (Inputs & Outputs)
- **eaui2026_v3.ipynb** — Main notebook, latest version
- **diccionario_variables.csv** — Data dictionary defining all columns and metadata
- **informe_final.pdf** — Final analysis report (output)

---

## Data Flow

```
Raw Data (SPSS 2008-2026)
          ↓ pyreadstat
    eaui2026_v3.ipynb
          ├→ GSE Derivation (socioeconomic classification)
          ├→ Variable Recoding (renaming, remapping values)
          ├→ Text Normalization (clean text fields)
          └→ Data Dictionary Reference
          ↓
    informe_final.pdf (Report Output)
```

**Key insight:** All data processing is **inside the notebook**. There is no separate ETL module, no data warehouse, no streaming pipeline. This is intentional for an exploratory survey analysis.

---

## Relationships

### Extracted (High Confidence, Explicit in Source)
- `pyreadstat` reads SPSS format files  
- Notebook imports `pyreadstat` and `pandas`
- Notebook implements GSE derivation and variable recoding  
- Data directory contains SPSS format files  
- Notebook loads raw data from `/data/sav/`

### Inferred (Reasonable but Not Explicit)
- Notebook references data dictionary for column definitions (confidence: 0.85)
- Processed data flows to final report generation (confidence: 0.8)
- GSE derivation is a specialization of variable recoding (confidence: 0.7, semantically similar)

### No Ambiguous Edges
All relationships are either clearly stated or reasonably inferred. No uncertain claims.

---

## Hyperedges (Multi-Way Relationships)

1. **Data Processing Stack**  
   Nodes: `eaui_v3_notebook`, `pyreadstat`, `pandas`, `Jupyter`  
   All four form the technical foundation for notebook-based analysis.

2. **Input Data**  
   Nodes: `/data/sav/`, `SPSS Format`, `EAUI 2026 Survey`  
   All three describe the raw input layer.

---

## What's Not Here

- **No other notebooks.** Versions `v2` and earlier are mentioned in docs but not extracted (files not in corpus).
- **No code structure.** AST extraction found zero code files (notebooks use JSON format, not in detection patterns).
- **No external dependencies beyond pandas/pyreadstat.** No databases, APIs, or remote services visible.
- **No test files or CI/CD.** Git hooks exist but no test suite detected.

---

## Observations

1. **Notebook-centric design is intentional.** For exploratory survey analysis, this is reasonable. All logic is in cells, no separate modules.

2. **Small, focused scope.** One main notebook, one data dictionary, one report output. No complex pipelines or orchestration.

3. **Long data history.** Survey runs since 2008; `/data/sav/` holds 19 years of SPSS files. Raw data unchanged; processed outputs change as recoding logic updates.

4. **Socioeconomic derivation is core logic.** GSE calculation dominates the processing section—this is the value-add on top of raw survey responses.

5. **Text normalization is explicit.** Using `re` and `unicodedata` suggests handling of Unicode issues (common in Spanish survey data).

---

## Recommendations

- **Extract notebook cells as separate entities** if graphify adds `.ipynb` detection (would surface cell-level logic and data flow).
- **Track variable transformations** to build lineage from raw columns (e.g., A10, A11) to final output columns.
- **Index the informe_final.pdf** once PDF parsing is enabled (would reveal analysis insights and conclusions).
- **Document GSE derivation rules** explicitly — currently buried in code; making it a first-class entity would aid auditability.

---

## Files Generated

- `graph.json` — Full node/edge graph in GraphRAG-ready format
- `index.html` — Interactive visualization (vis.js network)
- `GRAPH_REPORT.md` — This report

Open `index.html` in a browser to explore the graph interactively.
