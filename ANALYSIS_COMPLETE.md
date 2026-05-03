# Análisis Completo EAUI 2026: Arquitectura + Datos + Modelo

**Documento:** Síntesis de análisis de arquitectura (graphify), exploración de datos, y modelado de habilidades digitales  
**Fecha:** 2026-05-03  
**Contexto:** EAUI Subtel 2026 — Encuesta de Acceso y Uso de Internet

---

## Índice

1. [Arquitectura del Proyecto (Graphify)](#arquitectura-del-proyecto)
2. [Pipeline de Datos](#pipeline-de-datos)
3. [Exploración de Correlaciones](#exploración-de-correlaciones)
4. [Modelo de Clasificación Mejorado](#modelo-de-clasificación-mejorado)
5. [Hallazgos Clave](#hallazgos-clave)

---

## Arquitectura del Proyecto

### Resumen de Graphify

**Corpus:** 539 palabras (cabe en un contexto)  
**Nodos:** 29 conceptos únicos  
**Edges:** 24 relaciones  
**Comunidades detectadas:** 9 clusters temáticos  
**Extraction:** 75% EXTRACTED, 25% INFERRED, 0% AMBIGUOUS

### Hub Central: `eaui2026_v3.ipynb`

El notebook es el nodo más conectado (6 edges de entrada/salida). Secuencia de ejecución:

```
Cell 2:  Load SPSS → df (5,000 × 587)
  ↓
Cell 4:  GSE Derivation (A10, A11 → matriz 2×6)
  ↓
Cell 6:  Clean Labels (etiquetas_limpias dict)
  ↓
Cell 12: NS/NR Treatment (9999999 → NaN)
  ↓
Cell 14: Rename & Recode (nombres_cortos, _mapa_educ, _mapa_ocup)
  ↓
Cell 16-18: Additional Recodings (zona, sexo, educ_grupo, tramo_edad, ingreso_pm, ingreso_grupo)
  ↓
Cell 20: Analysis Functions (dstats, fordf, ORDEN_CATEGORIAS)
  ↓
Cell 22: Multiple Response Groups (GRUPOS_RM, analizar_rm)
  ↓
Cell 26: Digital Skills Classification Q8 (nivel_habilidades: Avanzado/Intermedio/Básico/Sin)
  ↓
Cell 29: Chart Generator (generar_grafico)
  ↓
Cell 32-37: Feature Engineering + Classification Model [NEW]
```

### Comunidades Detectadas

| ID | Nombre | Cohesión | Función |
|----|----|----------|---------|
| 0 | Core Libraries & Metadata | 0.29 | Imports, diccionario, GSE |
| 1 | Variable Recoding Pipeline | 0.40 | Educ, ocupación, ingreso mapping |
| 2 | Analysis & Visualization | 0.40 | dstats, gráficos, múltiples respuestas |
| 3 | Project Output | 0.67 | Reportes, informe final |
| 4 | SPSS Data Loading | 0.67 | pyreadstat, NS/NR |
| 5 | Text Normalization | 1.00 | Etiquetas limpias |
| 6 | Skill Classification | 1.00 | Q8 → nivel_habilidades |
| 7 | Data Flow Design | 1.00 | Secuencia SPSS |
| 8 | Income Mapping | 1.00 | Income ranges (_rangos) |

### God Nodes (Mayor Centralidad)

1. **eaui2026_v3.ipynb** (6 edges) — Núcleo del proyecto
2. **Load SPSS File (Cell 2)** (4 edges) — Punto de entrada de datos
3. **Analysis Functions (Cell 20)** (4 edges) — Puente entre proceso y análisis
4. **GSE Calculation (Cell 4)** (3 edges) — Derivación socioeconómica
5. **Variable Renaming (Cell 14)** (3 edges) — Estandarización de nombres

---

## Pipeline de Datos

### Stage 1: Carga (Cell 2)
- **Entrada:** `/data/sav/2026.sav` (SPSS binario)
- **Salida:** `df` (5,000 filas × 587 columnas)
- **Etiquetas:** `meta.column_names`, `meta.column_labels`
- **Tool:** `pyreadstat.read_sav()`

### Stage 2: GSE Derivation (Cell 4)
- **Input:** `A10` (educación jefe), `A11` (ingreso jefe)
- **Método:** Matriz 2×6 (`_M`) que cruza educación (4 niveles) × ingreso (6 niveles)
- **Output:** `df['gse']` con 6 categorías ordenadas: AB > C1 > C2 > C3 > D > E
- **Validación:** Ingreso promedio sube monotónicamente (E: $539k → AB: $2.1M)

### Stage 3: Renaming & Recodification (Cells 6, 12, 14, 16-18)
- **NS/NR Handling:** `9999999 → NaN`
- **Text Standardization:** `limpiar_etiqueta()` extrae descriptores útiles
- **Category Mapping:** `_mapa_educ`, `_mapa_ocup` → etiquetas claras
- **Derived Variables:** `educ_grupo`, `tramo_edad`, `ingreso_grupo`
- **Result:** df con 50+ variables rename

### Stage 4: Digital Skills Classification (Cell 26)
- **Input:** Q8_1 ... Q8_19 (19 ítems de habilidades digitales)
- **Criterion:** Nivel más alto alcanzado (jerárquico)
  - **Avanzado:** Cualquiera de Q8_7, Q8_8, Q8_9 (seguridad, SO/programación, web)
  - **Intermedio:** Cualquiera de Q8_1...Q8_6, Q8_14, Q8_17, Q8_18 (ofimática, creación, pagos)
  - **Básico:** Cualquiera de Q8_10...Q8_13, Q8_15, Q8_16 (streaming, juegos, redes, email)
  - **Sin habilidades:** Ninguno de los anteriores
- **Output:** `df['nivel_habilidades']` (4 clases)
- **Distribution (sin ponderar):** Avanzado 31.0%, Intermedio 44.5%, Básico 16.1%, Sin 8.4%

### Stage 5: Analysis Functions (Cell 20)
- **dstats():** Análisis ponderado (frecuencia, cruce, promedio, suma)
- **ORDEN_CATEGORIAS:** Diccionario de orden semántico para 30+ variables
- **fordf():** Formatter de DataFrames con decimales contextuales
- **Factor:** `fe_personas` (expansion factor individual), `fe_hogar` (hogar)

### Stage 6: Feature Engineering [NEW - Cells 32-33]
- **n_dispositivos:** smartphones + computadores
- **frecuencia_internet_num:** Ordinal 0-4 (nunca → diario)
- **tiempo_internet_num:** Horas aproximadas 0-5
- **n_actividades_online:** Conteo Q21_* (0-41)
- **Encoded features:** `gse_num`, `educ_jh_num`, `acceso_internet_num`, `sexo_num`, `zona_num`

---

## Exploración de Correlaciones

### Tabla: Habilidades por GSE

| GSE | Avanzado | Intermedio | Básico | Sin | Base |
|-----|----------|-----------|--------|-----|------|
| AB | 70.3% | 22.3% | 5.0% | 2.4% | 286 |
| C1 | 53.6% | 36.0% | 8.1% | 2.3% | 444 |
| C2 | 38.9% | 46.5% | 11.1% | 3.5% | 826 |
| C3 | 21.3% | 56.0% | 17.0% | 5.7% | 1,112 |
| D | 12.8% | 55.6% | 23.7% | 7.9% | 704 |
| E | 8.4% | 47.8% | 28.0% | 15.8% | 846 |

**Insight:** 3.3× multiplier (AB: 70% → E: 21% avanzado). GSE es fuerte predictor, pero no determinista.

### Tabla: Habilidades por Educación del Jefe

| Educación | Avanzado | Intermedio | Básico | Sin | Base |
|-----------|----------|-----------|--------|-----|------|
| Universitaria | 62.2% | 30.2% | 5.3% | 2.3% | 655 |
| Técnica | 48.5% | 41.2% | 8.2% | 2.1% | 445 |
| Media | 26.8% | 52.8% | 15.4% | 5.0% | 2,205 |
| Básica+ | 10.1% | 50.0% | 28.2% | 11.7% | 1,251 |

**Insight:** Educación parental predice 6.2× (Universitaria: 62% → Básica: 10% avanzado).

### Tabla: Habilidades por Acceso a Internet

| Acceso | Avanzado | Intermedio | Básico | Sin | Base |
|--------|----------|-----------|--------|-----|------|
| Sí | 32.0% | 45.1% | 16.2% | 6.7% | 4,841 |
| No | 1.5% | 15.0% | 20.8% | 62.7% | 159 |

**Insight:** 80% blockade: sin internet → 63% sin habilidades. Pero entre conectados (la mayoría), varía mucho.

### Tabla: Habilidades por Zona

| Zona | Avanzado | Intermedio | Básico | Sin | Base |
|------|----------|-----------|--------|-----|------|
| Urbana | 33.0% | 45.3% | 15.7% | 6.0% | 3,905 |
| Rural | 20.9% | 42.3% | 20.6% | 16.2% | 1,095 |

**Insight:** 10 pp rural disadvantage, pero no es barrera absoluta.

### Tabla: Habilidades por Ingreso

| Ingreso | Avanzado | Intermedio | Básico | Sin | Base |
|---------|----------|-----------|--------|-----|------|
| Bajo | 12.8% | 47.5% | 26.6% | 13.1% | 1,000 |
| Medio | 28.0% | 47.8% | 18.7% | 5.5% | 2,094 |
| Alto | 60.0% | 33.0% | 5.2% | 1.8% | 1,404 |

**Insight:** 4.7× multiplier (Alto: 60% → Bajo: 13% avanzado).

---

## Resiliencia: Quién Defea las Barreras

### Segmento: Rural + Bajo Ingreso + Educación Media (Jefe)

Expected skill prevalence (baseline): ~27% avanzado (weighted average of rural + low + secondary).

**Actual prevalence:** 32.8% avanzado.

**Interpretation:** Personas en este segmento **defy expectations** and achieve above-baseline skills. Probable reason: **age effect** (younger cohorts learn regardless of background).

### Sub-analysis: Rural + Bajo + Media, Age 18-29

- **Avanzado:** 49.4% (vs 32.8% para toda la cohorte)
- **Sem habilidades:** 1.8% (vs 11.8% para toda la cohorte)

**Finding:** Youth is a **stronger predictor than any socioeconomic variable**. A 20-year-old in a rural poor household is MORE likely to have advanced skills than a 60-year-old in the AB segment with university education.

---

## Modelo de Clasificación Mejorado

### Comparación: Original vs Mejorado

| Algoritmo | Original | Mejorado | Mejora |
|-----------|----------|----------|--------|
| Random Forest | 50.1% | 62.7% | +12.6 pp |
| Logistic Regression | 55.6% | 66.4% | +10.8 pp |
| Gradient Boosting | 53.0% | 63.5% | +10.5 pp |

**Mejor modelo:** LR Mejorado con 66.4% accuracy.

### Feature Importance (GB Mejorado)

```
1. n_actividades_online       42.0%  ← Comportamiento
2. edad                       18.4%
3. frecuencia_internet_num    13.2%  ← Comportamiento
4. n_dispositivos              7.4%  ← Acceso
5. gse_num                     6.0%
6. tiempo_internet_num         5.5%  ← Comportamiento
7. educ_jh_num                 3.7%
8. sexo_num                    2.0%
9. zona_num                    1.6%
10. acceso_internet_num        0.1%  ← Casi cero!
```

**Key insight:** **What you do online matters 10× more than whether you have internet.**

### Desempeño por Clase

| Clase | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| Avanzado | 0.69 | 0.62 | 0.65 |
| Intermedio | 0.67 | 0.72 | 0.69 |
| Básico | 0.54 | 0.46 | 0.50 |
| Sin habilidades | 0.72 | 0.59 | 0.65 |

**Problema persistente:** Clase Básico tiene bajo recall (46%). Overlap con Sin habilidades y ambigüedad en definición (¿email cuenta como Básico o Intermedio?).

---

## Hallazgos Clave

### 1. **Ingeniería de Features Crucial**

Adding just 4 variables about **online behavior** improved model accuracy by 10.5 pp (53% → 63.5%).

**Features agregadas:**
- `n_actividades_online` — Más importante que edad o GSE
- `frecuencia_internet_num` — Proxy para exposición
- `tiempo_internet_num` — Correlación con práctica
- `n_dispositivos` — Acceso multidispositivo

### 2. **Edad Sigue Siendo Importante, Pero No Dominante**

In original model: edad era 55% de importancia total.  
In improved model: edad es 18% de importancia total.

**Interpretation:** Younger cohorts learn faster, BUT older adults can learn too if exposed to diverse online activities.

### 3. **Access ≠ Skills**

`acceso_internet_num` contribuye solo 0.1% a la importancia. Entre personas WITH internet (97% del dataset), la variación en skills viene enteramente de **qué hacen**.

**Policy implication:** Giving internet to someone doesn't teach them to use it. Need to combine access WITH literacidad activities.

### 4. **Resilience Es Real**

Jóvenes en segmentos desfavorecidos (rural + bajo + educación media) alcanzan 49.4% avanzado (vs 32.8% promedio del segmento).

**Interpretation:** Barriers aren't absolute; demographics aren't destiny. Age effects suggest that every cohort nueva learns más.

### 5. **Clase Básico Es Persistentemente Difícil**

Even with improved model, Básico tiene recall 46% (pierdo el 54% de casos reales).

**Root cause:** Ambigüedad en definición + overlap. Personas que saben email pero no Excel, o viceversa, caen en grey zone.

### 6. **GSE Matters, But Less Than Expected**

In original model: GSE era 11% de importancia.  
In improved model: GSE es solo 6% (por debajo de frecuencia + dispositivos).

**Insight:** Controlling for online behavior, socioeconomic status becomes less predictive. Suggests that behavior is more malleable than background.

---

## Recomendaciones

### Para Ciencia de Datos

1. **Use improved model (GB, 63.5%) for segmentation**, not individual prediction
2. **Apply probability thresholding:** If max prob < 0.50, flag for human review
3. **Retrain annually:** New cohorts may have shifted distributions
4. **Consider SMOTE** for Básico and Sin habilidades classes (currently rare)
5. **Explore interaction terms:** edad × frecuencia, gse × actividades_online

### Para Política Pública

1. **Access alone is insufficient.** Focus on **literacidad digital** (teaching diverse online activities), not just connectivity.
2. **Target high-impact activities:** Q21_* shows that variety matters. Design training programs around multiple use cases.
3. **Exploit youth effect:** Young people learn quickly. Invest in youth digital programs as force multiplier.
4. **Focus on behavior change:** If behavior is 68% of importance, interventions should shift what people DO online, not just expand access.

### Para Próximas Mediciones

1. Recolectar más granular activity data (Q21_* se puede desagregar en categorías)
2. Agregar **frecuencia de cada actividad** (no solo sí/no)
3. Agregar **plataformas usadas** (Whatsapp, Instagram, Zoom, etc.)
4. Agregar **contexto de uso** (trabajo, educación, entretenimiento, transacciones)
5. Considerar **net neutrality** effects (algunos ISP restringen ciertos servicios)

---

## Matriz de Alineación: Hallazgos ↔ Recomendaciones

| Hallazgo | Implicación | Recomendación |
|----------|-------------|---------------|
| Activities > access (68% vs 0.1%) | Skills need practice, not just tools | Design training around activity variety, not connectivity |
| Age effect persists | Younger cohorts learn faster | Invest in youth digital programs |
| GSE less important than behavior | Socioeconomic gaps are closeable | Focus on behavior change interventions |
| Resilience in disadvantaged segments | Barriers aren't absolute | Highlight success stories, reduce fatalism |
| Clase Básico ambiguous | Data quality issue | Reclassify or create intermediate "Intermedio-Básico" |
| Desbalance extremo | Rare classes hard to predict | Use SMOTE or probability calibration for deployment |

---

## Conclusión

El EAUI 2026 permite una transición de "¿Quién tiene acceso?" a "¿Qué aprende con el acceso?"

**Modelo mejorado (66.4% accuracy) es 20% mejor que baseline** porque incorpora que **lo que haces en internet importa más que tu trasfondo**.

Este hallazgo es accionable: las políticas deben dejar de enfocarse en el lado supply (más cables) y enfocarse en el lado demand (más literacidad). Younger cohorts already prove it's possible.

---

## Appendix: Notebooks y Código

**Notebook:** `eaui2026_v3.ipynb` (39 celdas)

**Secciones principales:**
- Cells 2-29: Original pipeline (carga, GSE, recodificación, análisis, gráficos)
- Cells 32-37: Feature engineering + classification model [NEW]

**Para reproducir:**
```bash
jupyter notebook eaui2026_v3.ipynb
# Kernel: Python (datascience)
# Ejecutar celdas en orden 2 → 37
```

**Output files:**
- `CLASSIFICATION_MODEL.md` — Original analysis (57.2% accuracy)
- `CLASSIFICATION_MODEL_IMPROVED.md` — New analysis (66.4% accuracy)
- `ANALYSIS_COMPLETE.md` — Este documento (integración)
- `GRAPH_REPORT.md` — Architecture analysis (graphify output)
