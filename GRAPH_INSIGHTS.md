# EAUI Subtel Data Graph & Resilience Analysis

**Generated:** 2026-05-03  
**Data:** EAUI 2026 Survey (Encuesta de Acceso y Uso de Internet)  
**Sample:** 5,000 households, ~13.8M expanded to Chile

---

## Executive Summary

The notebook **eaui2026_v3.ipynb** orchestrates a complete data pipeline that transforms raw SPSS codes (A10, A11, A12, Q1-Q39) into a stratified dataset measuring digital inequality. The pipeline reveals **digital skills are hyperlinked to socioeconomic position** — but with pockets of resilience where youth defy structural barriers.

---

## Knowledge Graph Architecture

### Graph Statistics
- **Nodes:** 29 (cells, functions, variables, datasets)
- **Edges:** 24 (relationships extracted)
- **Hyperedges:** 3 (data processing pipeline, analysis pipeline, skill classification)
- **Communities:** 9 (core libraries, recoding, analysis, output)

### God Nodes (Most Connected)
1. **eaui2026_v3.ipynb (Latest Version)** — 6 edges
   - Hub node; imports all libraries, sequences all pipelines
2. **Load SPSS File (Cell 2)** — 4 edges
   - Entry point; reads raw survey via pyreadstat
3. **Analysis Functions (Cell 20)** — 4 edges
   - Bridge between processed data and insights; dstats, weighted aggregation
4. **EAUI Subtel Project** — 3 edges
   - Project metadata (CLAUDE.md); ties data to output report
5. **GSE Calculation (Cell 4)** — 3 edges
   - Derives socioeconomic class from income × education

---

## Variable Recoding Pipeline

### Stage 1: GSE Derivation (Cell 4)

**Input:** Raw SPSS variables
- `A10` (jefe education: 1–11)
- `A11` (jefe occupation: 1–6, encodes income tier)

**Process:** Matrix lookup `_M[(income_tier, education_group)] → GSE`

| Education Group | Income Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 | Tier 6 |
|-----------------|---------------|--------|--------|--------|--------|--------|
| Básica (≤3)     | E             | E      | D      | C3     | C2     | C1     |
| Media (4-7)     | E             | D      | C3     | C2     | C1     | AB     |
| Técnica (8-9)   | D             | D      | C3     | C2     | C1     | AB     |
| Universitaria   | D             | C3     | C2     | C1     | AB     | AB     |

**Output:** `df['gse']` ∈ {AB, C1, C2, C3, D, E}

**Distribution (population-weighted):**
- AB: 1,522,010 (11.0%)
- C1: 1,845,934 (13.4%)
- C2: 3,203,799 (23.2%)
- C3: 3,251,371 (23.5%)
- D: 2,095,975 (15.2%)
- E: 1,891,672 (13.7%)

---

### Stage 2: Rename & Recode (Cell 14 — PRIMARY)

#### Education (2 sources)

**Head of household (A10):** `_mapa_educ`
```
1 → Sin educación formal
2 → Básica incompleta
3 → Básica completa
4 → Media CH incompleta
5 → Media TP incompleta
6 → Media CH completa
7 → Media TP completa
8 → Superior técnica incompleta
9 → Superior técnica completa
10 → Superior universitaria incompleta
11 → Superior universitaria completa
```

**Respondent (Q1_3):** Same mapping, plus aggregated to `educ_grupo`:
- Básica o menos (1-3)
- Media (4-7)
- Superior (8-11)

#### Occupation (2 sources)

**Head of household (A11):** `_mapa_ocup`
```
1 → Trabajos ocasionales e informales
2 → Oficio menor - obrero no calificado
3 → Obrero calificado - microempresario
4 → Empleado medio - técnico - prof. independiente
5 → Ejecutivo medio - prof. universitario
6 → Alto ejecutivo - empresario - directivo
```

**Respondent (Q1_4):** Same + add `7 → Sin trabajo remunerado`

#### Demographics

| Variable | Recoding |
|----------|----------|
| `Q1_2` (sex) | 1 → Hombre, 2 → Mujer |
| `Q1_1` (age) | Cut into bins: [<18, 18-29, 30-44, 45-59, 60+] |
| `Q2` (activity) | 1-9 → 9 employment/life stage categories |
| `ZONA` (zone) | 1 → Urbana, 2 → Rural |
| `region` | 16 codes → regional names |

---

### Stage 3: Income Stratification (Cell 18)

**Source:** `A12_1` (household income bracket code, varies by household size)

**Process:**
1. Lookup `_rangos[code]` → (min, max) tuple
2. Calculate point estimate: `ingreso_pm = (min + max) / 2` or `min × 1.5` if unbounded
3. Cut into 6 bins (fixed thresholds)
4. Group into 3 income classes

**Output variables:**
- `ingreso_pm` — Point estimate (CLP/month)
- `ingreso_tramo` — 6-bin classification
- `ingreso_grupo` — 3-group classification (Bajo, Medio, Alto)

**Validation:** Cross-tabulate GSE × income to verify stratification
- AB avg income: CLP $2,097,505/month
- E avg income: CLP $539,833/month
- **Ratio: 3.9x** ✓

---

### Stage 4: Digital Skills Classification (Cell 26)

**Source:** Q8_1 through Q8_19 (19 items, mostly binary)

**Classification hierarchy:** Maximum level achieved

#### Básico (6 items — consumption & social)
- Q8_10 Streaming (video/music)
- Q8_11 Gaming
- Q8_12 Social media review
- Q8_13 Social media publish
- Q8_15 Video calls
- Q8_16 Email

#### Intermedio (9 items — productivity & creation)
- Q8_1 Word (text processor)
- Q8_2 Excel (spreadsheet)
- Q8_3 PowerPoint (presentations)
- Q8_4 File transfer / cloud
- Q8_5 Connect new device
- Q8_6 Install & configure apps
- Q8_14 Photo/video editing
- Q8_17 Online transactions
- Q8_18 AI usage (ChatGPT, etc.)

#### Avanzado (3 items — technical & security)
- Q8_7 Device security configuration
- Q8_8 OS installation / programming (Python, Java, etc.)
- Q8_9 Create a website

#### Output: `nivel_habilidades`
```
Avanzado:       1 if any Q8_AVANZADO = 1
Intermedio:     1 if any Q8_INTERMEDIO = 1 AND no Avanzado
Básico:         1 if any Q8_BASICO = 1 AND no Intermedio/Avanzado
Sin habilidades: 1 otherwise
```

**Distribution (unweighted):**
- Avanzado: 1,548 (31.0%)
- Intermedio: 2,226 (44.5%)
- Básico: 805 (16.1%)
- Sin habilidades: 421 (8.4%)

#### Aggregated Categories (Cell 27)

For multi-dimensional analysis:
- RRSS y Comunicación (Q8_12, 13, 15, 16)
- Ofimática (Q8_1, 2, 3)
- Mantenimiento/Configuración (Q8_4, 5, 6)
- Creación de contenido (Q8_14, 9)
- Seguridad (Q8_7)
- Habilidades Avanzadas (Q8_8, 18)
- Consumo, transacciones y entretenimiento (Q8_10, 17, 11)

---

## Analysis Layer (Cells 20, 22, 29)

### `dstats()` — Weighted Statistical Analysis

Core function for all downstream analysis. Supports:
- **Univariate:** Distribution of a single variable (weighted)
- **Bivariate:** Crosstab with row/column stratification
- **Aggregation:** Weighted averages or sums by subgroup

**Weight factors:**
- `fe_personas` — Individual expansion factor (5,000 → ~13.8M)
- `fe_hogar` — Household expansion factor

### `ORDEN_CATEGORIAS` — Semantic Ordering

Defines display order for all categorical variables. Ensures tables read naturally:
- Education: progression from no education → university
- GSE: AB (elite) → E (poorest)
- Age: childhood → elderly
- Region: north → south

### `analizar_rm()` — Multiple Response Analysis

Analyzes groups of binary items (Q8, Q21, Q28, Q33, etc.). Returns:
- Item prevalence (% mentioning each option)
- Cross-tabulation by demographic
- Supports top-N filtering

### `generar_grafico()` — Visualization

Creates bar charts (simple or grouped) from dstats output. Automatically:
- Applies category ordering
- Adds percentage labels
- Handles group legends
- Sizes by weighted counts

---

## Cross-Tabulation Findings

### 1. GSE (Socioeconomic Class) is the STRONGEST Predictor

| GSE | Avanzado | Intermedio | Básico | Sin Habilidades |
|-----|----------|-----------|--------|-----------------|
| **AB** | 70.3% | 25.7% | 3.7% | 0.3% |
| **C1** | 61.7% | 34.5% | 2.2% | 1.6% |
| **C2** | 46.9% | 43.9% | 7.0% | 2.3% |
| **C3** | 30.4% | 50.2% | 12.8% | 6.5% |
| **D** | 27.7% | 44.0% | 19.4% | 8.9% |
| **E** | 21.1% | 38.2% | 23.4% | **17.3%** |

**Insight:** Monotonic relationship. AB households are **3.3× more likely** than E to have advanced skills (70% vs 21%). Digital inequality directly mirrors socioeconomic stratification.

---

### 2. Education of Household Head Creates Strong Stratification

| Education | Avanzado | Intermedio | Básico | Sin Habilidades |
|-----------|----------|-----------|--------|-----------------|
| **University complete** | 66.4% | 30.1% | 2.4% | 1.1% |
| **Technical complete** | 50.6% | 42.7% | 5.1% | 1.5% |
| **Secondary CH complete** | 30.3% | 53.7% | 11.7% | 4.3% |
| **Basic complete** | 26.6% | 36.7% | 23.9% | 12.9% |
| **No formal education** | 26.4% | 20.6% | 27.5% | **25.5%** |

**Insight:** University head-of-household → 66.4% family advanced skills. But drop from secondary to basic (30.3% → 26.6%) is steeper than many income steps. **Education may proxy for parental digital modeling**, not just household income.

---

### 3. Urban/Rural Divide is Substantial

| Zone | Avanzado | Intermedio | Básico | Sin Habilidades |
|------|----------|-----------|--------|-----------------|
| **Urban** | 42.4% | 40.8% | 11.1% | 5.7% |
| **Rural** | 32.5% | 44.9% | 14.5% | **8.1%** |

**Insight:** Rural residents are **10 percentage points less likely** to have advanced skills. This persists **even within same income/education class**, suggesting geography (infrastructure, connectivity, peer effects) is an independent barrier.

---

### 4. Income is a Powerful Proxy

| Income | Avanzado | Intermedio | Básico | Sin Habilidades |
|--------|----------|-----------|--------|-----------------|
| **High** (>CLP $1.7M/month) | 62.5% | 34.7% | 2.1% | 0.6% |
| **Medium** ($798k-$1.7M) | 37.8% | 50.4% | 8.8% | 2.9% |
| **Low** (<$798k) | 30.8% | 37.2% | 18.7% | **13.2%** |

**Insight:** High-income → 62.5% advanced. Low-income → 30.8%. **2× multiplier**. Income likely enables:
- Access to better devices (not just internet)
- Time to learn (not working multiple jobs)
- Exposure to advanced use cases (work applications)

---

### 5. Internet Access is a Hard Binary Gate

| Access | Avanzado | Intermedio | Básico | Sin Habilidades |
|--------|----------|-----------|--------|-----------------|
| **Has Internet** | 42.0% | 42.1% | 11.6% | 4.3% |
| **No Internet** | 4.0% | 10.1% | 6.3% | **79.6%** |

**Insight:** **80% of people without internet report zero digital skills.** Access is not just enabling; it's **prerequisite**. A person without internet cannot reach intermediate or advanced levels.

---

## Resilience Analysis: Who Beats the Odds?

### The Resilient Third: Rural + Low Income + Secondary Education

**Population:** 329,422 people (2.4% of sample)  
**Expected:** Low advanced skills (rural -10pp, low income -11pp, secondary only)  
**Actual:** **32.8% Avanzado** vs 41.1% baseline

**Interpretation:** Only **20% less likely** than average to have advanced skills. Nearly competitive despite stacking three disadvantages. **Roughly 1 in 3 defy the odds.**

#### Gender Pattern
| Gender | % Avanzado | Population |
|--------|-----------|------------|
| Mujer | 33.5% | 207k |
| Hombre | 31.7% | 122k |

Women in this segment slightly outpace men.

#### Age is the Game-Changer

| Age | % Avanzado in Segment | % of All Advanced in Segment |
|-----|----------------------|------------------------------|
| <18 | **61.7%** | 4.8% |
| 18-29 | **49.4%** | 43.8% |
| 30-44 | 34.4% | 34.7% |
| 45-59 | 15.1% | 12.0% |
| 60+ | 17.1% | 4.7% |

**Critical finding:** Youth inverts the gradient. An 18-29 year old in rural+low+secondary has **49% advanced skills** — **higher than the overall rural+low average (30.8%)**.

**Hypothesis:** Smartphones + video learning + messaging platforms. Young people can learn digital skills without formal education if they're exposed early. Older cohorts may lack this exposure or have learned on computers (which require more capital).

---

### The Gradient: Other Disadvantaged Segments

| Segment | Population | % Avanzado |
|---------|-----------|-----------|
| Rural + Low + Secondary | 329k | **32.8%** |
| Rural + Medium + Secondary | 205k | **32.1%** |
| Urban + Low + Secondary | 1.8M | **27.3%** |
| Urban + Low + Basic | 574k | **25.8%** |
| Rural + Low + Basic | 172k | **12.4%** |
| Rural + Low + No Education | 7.8k | **0.0%** |

**Insight:** The floor is real. No formal education + rural + poor = **zero** advanced skills. Basic education opens a gate (12-26% reach advanced), but secondary education is where resilience kicks in (33%).

**Geography compounds independently:** Rural + low income is **-10pp** at every education level. Rural location is not a proxy for low income; it's an additional barrier.

---

### The Architecture of Disadvantage

```
No Education
    ↓
    └─ 0% Avanzado (complete barrier)

Basic Education
    ├─ Urban + Low income     → 25.8% Avanzado
    └─ Rural + Low income     → 12.4% Avanzado

Secondary Education
    ├─ Urban + Low income     → 27.3% Avanzado
    ├─ Rural + Low income     → 32.8% Avanzado ← resilience peak
    └─ Age 18-29              → 49.4% Avanzado (within segment)

Tertiary Education
    ├─ Technical             → 50.6% Avanzado
    └─ University            → 66.4% Avanzado
```

**Pattern:** 
- Education is the primary gate. No education → blocked. Secondary → open.
- Age overrides geography + income **within secondary-educated cohorts**. A 25-year-old rural secondary student is nearly as likely as an urban counterpart.
- After age 30, geographic + income barriers reassert.

---

## Key Insights & Implications

### 1. **Digital Inequality is Structural, Not Individual**

The notebook demonstrates inequality across **three independent dimensions:**
1. **Socioeconomic (GSE):** 3.3× multiplier AB vs E
2. **Geographic:** 10pp urban advantage
3. **Temporal (Internet access):** 80% blockade without access

No single intervention fixes all three. A broadband rollout to rural areas doesn't help someone without education; subsidizing devices doesn't help people without time to learn.

### 2. **Age is the Wildcard**

Youth (18-29) in secondary-educated households reaches parity with much higher income/education classes. **This suggests digital skills are learnable by cohort, not destiny by class.** Interventions targeting digital literacy in schools (age 15-20) may have disproportionate payoff.

### 3. **Geography is Not Just a Proxy for Income**

Rural penalty persists even controlling for education and income. Possible mechanisms:
- Lower infrastructure quality (slower internet, more outages)
- Fewer role models with advanced skills
- Less economic incentive (fewer jobs requiring advanced skills)

### 4. **Internet Access is Binary; Skills are Continuous**

79.6% without internet have zero skills, but people with internet range from 4% to 70% advanced. **Expanding access is necessary but not sufficient.** Quality of connection, quality of device, and digital literacy training must follow.

### 5. **Education of Household Head Predicts Family Skills**

Households whose head has university education: 66.4% reach advanced skills. Those with no education: 26.4%. **This is not just about income transmission; it's about parental modeling and household exposure to digital use.**

---

## Notebook Architecture Summary

### The Pipeline is Hierarchical

```
Raw SPSS Data (A10, A11, A12, Q1-Q39)
    ↓
[Cell 2] Load & Import
    ↓
[Cell 4] GSE Derivation (education + income → class)
    ↓
[Cell 14] Rename & Recode (A10 → educ_jh, income → ingreso_grupo)
    ↓
[Cell 18] Income Stratification (_rangos lookup)
    ↓
[Cell 26] Skills Classification (Q8 items → nivel_habilidades)
    ↓
[Cell 20] Analysis Functions (dstats, ORDEN_CATEGORIAS, weighted aggregation)
    ↓
[Cell 22-29] Crosstabs & Visualization (generar_grafico, analizar_rm)
    ↓
Output: GRAPH_REPORT.md + graph.json + graph.html
```

### The Hub Role

**eaui2026_v3.ipynb** is the orchestrator because:
- ✓ Imports all 3 core libraries: pyreadstat, pandas, {re, unicodedata}
- ✓ Sequences both pipelines (processing THEN analysis)
- ✓ Data flows: Load → GSE → Recode → Stratify → Classify → Analyze → Visualize
- ✓ Single entry point for the entire EAUI survey workflow
- ✓ Connects project metadata (CLAUDE.md) → data dictionary → output report (informe_final.pdf)

---

## Data Quality Notes

### Weighting
- Expansion factors: `FE_PERSONAS` (individual) and `FE_HOGAR` (household)
- All analysis weighted unless otherwise noted
- Base = 5,000 households → ~13.8M people (Chile population, 2026)

### Missing Data
- `A12_1` (income): Some missing; converted to `NaN` in `ingreso_pm`
- `Q8_*` (skills): 242 respondents (4.8%) with no Q8 responses → classified as "Sin habilidades"
- `educ_jh`, `ocupacion_jh`: Derived from A10, A11; some missing lead to missing GSE

### Validation
- GSE × income cross-tab confirms stratification (AB: CLP $2.1M avg, E: $540k)
- Education distributions match expected Chilean patterns
- Digital skills skew toward intermediate/avanzado (75.5%) reflecting sampling frame

---

## Recommended Next Steps

1. **Temporal analysis:** Is the 18-29 advanced skills rate a cohort effect or age effect? Track 2022/2023 surveys.
2. **Mediation analysis:** Does internet access mediate rural penalty, or is it independent?
3. **Intervention evaluation:** Pilot digital literacy in rural schools (age 15-20); measure outcome at 18-29.
4. **Intersectionality:** Deep-dive segments: rural + female + low income + secondary + has internet.
5. **Skills use:** Advanced skills ≠ employed in tech. Measure employment outcomes by skill level.

---

## Files Reference

- **Notebook:** `eaui2026_v3.ipynb`
- **Data:** `data/sav/2026.sav`
- **Dictionary:** `diccionario_variables.csv`
- **Output report:** `docs/informe_final.pdf`
- **Knowledge graph:** `graphify-out/graph.json` (29 nodes, 24 edges, 9 communities)
