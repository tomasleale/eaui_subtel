# Codebase Structure

**Analysis Date:** 2026-04-27

## Directory Layout

```
/Users/tomas/github/eaui_subtel/
├── eaui2026_v2.ipynb              # PRIMARY: Production notebook (sections 1–10 setup + 11+ analysis)
├── eaui2026.ipynb                 # ARCHIVED: Draft notebook (reference only, do not use)
├── CLAUDE.md                       # Project instructions & weighting guide
├── readme.md                       # Repository description, variable definitions
├── AGENTS.md                       # Agent metadata (brief)
├── GEMINI.md                       # Gemini-specific instructions
├── diccionario_variables.csv       # Searchable variable dictionary (587 variables)
├── data/                           # Data directory
│   ├── sav/                        # SPSS source files (authoritative)
│   │   ├── 2008.sav
│   │   ├── 2011.sav
│   │   ├── 2012.sav
│   │   ├── 2013.sav
│   │   ├── 2015.sav
│   │   ├── 2016.sav
│   │   ├── 2017.sav
│   │   ├── 2018.sav
│   │   ├── 2024.sav
│   │   ├── 2025.sav
│   │   └── 2026.sav                # CURRENT: 5,000 rows × 587 columns
│   ├── xlsx/                       # Excel exports of raw data
│   └── csv/                        # CSV versions (if any)
├── docs/                           # Documentation output
├── .planning/                      # Project planning & roadmap
│   ├── codebase/                   # THIS DIRECTORY: GSD analysis outputs
│   │   ├── ARCHITECTURE.md         # High-level design & data flow
│   │   ├── STRUCTURE.md            # THIS FILE: Directory layout & module breakdown
│   │   ├── STACK.md                # Technology stack (TBD)
│   │   ├── INTEGRATIONS.md         # External APIs (TBD)
│   │   ├── CONVENTIONS.md          # Coding style patterns (TBD)
│   │   ├── TESTING.md              # Test patterns (TBD)
│   │   └── CONCERNS.md             # Technical debt & issues (TBD)
│   ├── PROJECT.md                  # Problem statement, success criteria
│   ├── REQUIREMENTS.md             # Feature specifications
│   ├── ROADMAP.md                  # Phase schedule & milestones
│   ├── STATE.md                    # Current phase status & progress
│   └── config.json                 # GSD configuration
├── .claude/                        # Claude Code agent configuration
│   └── skills/                     # Skill definitions for code agents
│       ├── explore-codebase.md
│       ├── review-changes.md
│       ├── refactor-safely.md
│       └── debug-issue.md
├── .kiro/                          # Kiro IDE configuration
│   ├── settings/
│   └── steering/
│       └── code-review-graph.md    # Code graph documentation
├── .code-review-graph/             # Code review graph cache (auto-generated)
├── .git/                           # Git repository
├── .gitignore                      # Git ignore rules
└── .env, .env.* (if present)       # Environment configuration (NOT COMMITTED)
```

## Directory Purposes

**`eaui2026_v2.ipynb`** (PRIMARY)
- Purpose: Main data analysis notebook
- Contains: 36 cells organized into 10 mandatory setup sections + 26 analysis sections
- Key sections: Carga (1), GSE derivado (2), Etiquetas limpias (3), NS/NR (5), Renombrado (6), Recodificaciones (7), Ingreso (8), Funciones (9), Grupos RM (10), Análisis (11+)
- Execution: Must run sections 1–10 before any analysis (11+)

**`eaui2026.ipynb`** (ARCHIVED)
- Purpose: Historical reference only (deprecated draft)
- Contains: Earlier version with different variable encodings
- Usage: Do NOT use for active analysis; refer to only if investigating historical decisions

**`data/sav/`** (Authoritative Source)
- Purpose: SPSS binary files for all 11 survey waves (2008–2026)
- Contains: 11 `.sav` files with raw survey responses
- Current: `2026.sav` is loaded in section 1 of `eaui2026_v2.ipynb`
- Access: `pyreadstat.read_sav()` extracts df + metadata

**`data/xlsx/`**
- Purpose: Excel exports of raw data for manual inspection
- Contains: 10 files covering main survey years
- Usage: Backup/reference only; notebook loads from `.sav` authoritative source

**`data/csv/`**
- Purpose: CSV versions (if processed)
- Contains: May include pre-processed outputs like `2026_procesado.csv`
- Usage: Checkpoint for external tool validation

**`diccionario_variables.csv`**
- Purpose: Searchable variable reference
- Contains: 587 rows (one per variable) with columns: variable, etiqueta, tipo, missing_count
- Usage: Look up variable codes and labels without loading SPSS metadata
- Format: CSV with headers `variable,etiqueta,tipo,nulls`

**`.planning/codebase/`** (GSD Analysis Output)
- Purpose: Codebase documentation written by GSD agents
- Contains: ARCHITECTURE.md, STRUCTURE.md, STACK.md, INTEGRATIONS.md, CONVENTIONS.md, TESTING.md, CONCERNS.md
- Usage: Reference for future code modifications, architecture decisions, test patterns

**`.planning/PROJECT.md`**
- Purpose: Project scope, problem statement, success criteria
- Contains: Analytical goals (explain internet access determinants), constraints (exclude tech proxies), in-scope/out-of-scope items
- Audience: SUBTEL policy makers, government stakeholders

**`.planning/REQUIREMENTS.md`**
- Purpose: Feature specifications and acceptance criteria
- Contains: Data quality checks, analysis types, visualization requirements

**`.planning/ROADMAP.md`**
- Purpose: Phase schedule and milestone tracking
- Contains: Timeline (2026-04-25 → 2026-05-09), phase breakdown, deliverables

**`.planning/STATE.md`**
- Purpose: Current phase status and progress
- Contains: Which phases complete, which in progress, blockers

**`.claude/skills/`** (Agent Skill Definitions)
- Purpose: Reusable agent recipes for code tasks
- Contains: SKILL.md index + `rules/*.md` files defining patterns for code exploration, review, refactoring, debugging
- Usage: Claude agents check this directory to apply project-specific conventions during code generation

**`.kiro/steering/code-review-graph.md`**
- Purpose: Code review graph configuration and documentation
- Contains: How to query the code graph, impact analysis patterns
- Usage: MCP server configuration for incremental code analysis

## Key File Locations

**Entry Points:**
- `eaui2026_v2.ipynb`: Main notebook (execute sections 1–10, then 11+)
- `data/sav/2026.sav`: Raw data source (loaded in cell 2 of eaui2026_v2.ipynb)

**Configuration:**
- `CLAUDE.md`: Setup instructions, weighting guide, common mistakes
- `readme.md`: Project overview, variable reference table
- `.planning/PROJECT.md`: Problem statement and success criteria
- `.env` (if present): Environment configuration with API keys / credentials (NOT in git)

**Core Logic:**
- `eaui2026_v2.ipynb`, cell 4: GSE derivation (lookup tables)
- `eaui2026_v2.ipynb`, cell 6: Label cleaning regex
- `eaui2026_v2.ipynb`, cell 14: Column renaming (`nombres_cortos` dict)
- `eaui2026_v2.ipynb`, cell 16: Recodification maps (numeric → text)
- `eaui2026_v2.ipynb`, cell 18: Income derivation (band midpoints)
- `eaui2026_v2.ipynb`, cell 20: Analysis functions (`dstats()`, `fordf()`, `ORDEN_CATEGORIAS`)
- `eaui2026_v2.ipynb`, cell 22: Multiple-response groups (`GRUPOS_RM`, `analizar_rm()`)

**Testing & Analysis:**
- `eaui2026_v2.ipynb`, cell 25+: Exploratory analysis cells (frequency tables, cross-tabs)
- `eaui2026_v2.ipynb`, cell 29: Digital skills classification and validation
- `eaui2026_v2.ipynb`, cell 30: MCA visualization
- `eaui2026_v2.ipynb`, cell 32: Static matplotlib plot generator
- `eaui2026_v2.ipynb`, cell 35: Interactive Plotly chart generator

## Naming Conventions

**Files:**
- Notebooks: `eaui{YEAR}[_v{VERSION}].ipynb` (e.g., `eaui2026_v2.ipynb`)
- Data sources: `{YEAR}.sav` (SPSS binary), `{YEAR}.csv` (CSV export)
- Documentation: UPPERCASE.md (e.g., CLAUDE.md, ARCHITECTURE.md)
- Config: lowercase_snake_case.json (e.g., config.json, .mcp.json)

**Notebook Cells:**
- Section headers: Markdown cell with `## N. Título` (e.g., `## 1. Carga del archivo`)
- Section content: Code cell immediately following header
- Comments: Inline `# Comentario` at top of data transformation cells

**Variables in Notebook:**
- DataFrames: `df` (main working df), `meta` (SPSS metadata), `df_acm` (complete-case subset for MCA)
- Dictionaries: `ORDEN_CATEGORIAS`, `GRUPOS_RM`, `etiquetas_limpias`, `nombres_cortos`
- Helper functions: `dstats()`, `analizar_rm()`, `fordf()`, `_ordenar()`, `generar_grafico()`, `crear_grafico_interactivo()`
- Private/internal: `_educ_g()`, `_M` (GSE mapping), `_rangos` (income bands), `_cols_b` / `_cols_i` / `_cols_a` (skill level columns)

**Column Names (After Section 6 Renaming):**
- Original SPSS codes: `COD_REGION`, `Q1_2`, `P11`, `A10`, `A11`, etc.
- Short names: `region`, `sexo`, `pago_mensual_internet`, `educ_jh`, `ocupacion_jh`, etc.
- Weight columns: `fe_hogar`, `fe_personas`, `pond_hogar`, `pond_personas`
- Derived columns: `gse`, `educ_grupo`, `tramo_edad`, `ingreso_pm`, `ingreso_tramo`, `ingreso_grupo`, `nivel_habilidades`

**Categorical Value Conventions (After Section 7 Recodification):**
- Gender: `'Hombre'`, `'Mujer'`
- Zone: `'Urbana'`, `'Rural'`
- Education group: `'Básica o menos'`, `'Media'`, `'Superior'`
- Age tranche: `'Menor de 18'`, `'18-29'`, `'30-44'`, `'45-59'`, `'60 y más'`
- GSE: `'AB'`, `'C1'`, `'C2'`, `'C3'`, `'D'`, `'E'` (high to low)
- Binary yes/no: `'Sí'`, `'No'`
- Access type: `'ADSL'`, `'Cable/Módem'`, `'Fibra óptica'`, `'Inalámbrica'`, etc.

## Where to Add New Code

**New Analysis (e.g., a new segmentation):**
- Location: Add new cell after section 11 in `eaui2026_v2.ipynb`
- Prerequisite: Sections 1–10 must be executed
- Pattern: Call `dstats(df, variable, ..., factor=...)` or `analizar_rm(grupo, ...)`
- Example:
  ```python
  # Edad por acceso a internet
  dstats(df, 'tramo_edad', tipo='cruzada', cruce='acceso_internet_hogar', factor='fe_personas', estilo=True)
  ```

**New Derived Variable (e.g., skill level sub-category):**
- Location: Add logic after section 8 but before section 9 in `eaui2026_v2.ipynb`
- Pattern: Use `df.apply()` or `df.map()` to create new column
- Prerequisite: All columns used in derivation must exist and be in final form (text labels)
- Example (for a new variable):
  ```python
  df['mi_variable'] = df.apply(lambda row: ..., axis=1)
  ```

**New Multiple-Response Group (e.g., Q26 activities):**
- Location: Add entry to `GRUPOS_RM` dict in section 10 (`eaui2026_v2.ipynb`, cell 22)
- Pattern: `'Q26': ('Descripción de Q26', [cols starting with 'Q26_'])`
- Prerequisite: Columns must exist in df after renaming (section 6)
- Example:
  ```python
  'Q26': ('Actividades en línea el mes pasado', [c for c in _c if c.startswith('Q26_')])
  ```

**New Analysis Function:**
- Location: Add function definition to section 9 (`eaui2026_v2.ipynb`, cell 20) or section 10 (cell 22)
- Pattern: Accept `data_df` and `factor` parameters; return DataFrame or Styler
- Prerequisite: Must use `ORDEN_CATEGORIAS` for ordering, `GRUPOS_RM` for group definitions
- Example:
  ```python
  def mi_funcion(data_df, variable, factor, estilo=True):
      # Logic here
      return fordf(result_df, titulo=...) if estilo else result_df
  ```

**New Visualization:**
- Location: Add cell after section 11 in `eaui2026_v2.ipynb`
- Pattern: Call `generar_grafico()` (matplotlib) or `crear_grafico_interactivo()` (Plotly) or use seaborn/matplotlib directly
- Example:
  ```python
  generar_grafico('sexo', cruce='gse', factor='fe_personas', titulo='Sexo por GSE')
  ```

**New Data Processing Step:**
- Location: Add new section (e.g., "11.5. Procesamiento especial") between existing sections
- Pattern: Mutate df in-place or create new derived columns; do NOT break section 1–10 sequence
- Prerequisite: Document any new dependencies (e.g., "requires section 8 to be complete")
- Example:
  ```python
  # 11.5. Procesamiento especial
  df['nueva_derivada'] = df['col1'].combine(df['col2'], lambda x, y: ...)
  ```

## Special Directories

**`.code-review-graph/`**
- Purpose: Auto-generated code knowledge graph cache
- Generated: Yes (by code-review-graph MCP server on file changes)
- Committed: No (in `.gitignore`)
- Regenerate: Delete and re-run analysis (graph rebuilds on next query)

**`.git/`**
- Purpose: Git version control history
- Generated: Yes (git init creates it)
- Committed: No (standard .git exclusion)
- Usage: Track notebook changes, commits, branch history

**`.idea/`**
- Purpose: JetBrains IDE configuration (PyCharm, IntelliJ)
- Generated: Yes (IDE creates on project open)
- Committed: No (in `.gitignore`)
- Usage: IDE settings (ignored by git)

**`docs/`**
- Purpose: Documentation output directory
- Generated: Can be generated from notebooks (e.g., nbconvert)
- Committed: Conditional (commit if stable docs, not if auto-generated)
- Usage: HTML exports, markdown conversions

---

*Structure analysis: 2026-04-27*
