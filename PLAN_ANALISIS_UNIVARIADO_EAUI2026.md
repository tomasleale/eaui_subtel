# Plan de Análisis Univariado — EAUI 2026

**Base de datos:** `encuesta_uso_internet_chile_2026.csv` (5.000 casos, ~500 variables)
**Diccionario:** `EAUI_2026_Diccionario_Variables.csv`
**Notebook sugerido:** `00_descriptivo_univariado.ipynb`
**Documento complementario:** `PLAN_ANALISIS_EAUI2026.md` (bivariado, multivariado, inferencial y ML)

Este plan describe la estrategia para caracterizar cada variable de la encuesta de forma individual. Es la primera capa analítica y debe completarse antes de pasar a los cruces bivariados, porque permite detectar problemas de calidad de datos, distribuciones inesperadas y casos extremos que pueden afectar análisis posteriores.

---

## 0. Preparación previa

**Cargar la base y el diccionario.** El diccionario es la guía maestra: indica el tipo de cada variable, su universo (universal o filtrada), valores válidos y porcentaje de faltantes esperado.

```python
import pandas as pd
df = pd.read_csv("encuesta_uso_internet_chile_2026.csv")
dicc = pd.read_csv("EAUI_2026_Diccionario_Variables.csv")
```

**Definir tipos correctamente.** Pandas no lee bien los tipos por defecto. Antes de describir conviene:

- Convertir variables ordinales a `pd.Categorical` con orden explícito (`gse`, `tramo_edad`, `nivel_habilidades`, `educ_grupo`, `ingreso_grupo`).
- Marcar las binarias 0/1 como tales (no como float64).
- Asegurarse de que las fechas sean `datetime`.

**Identificar el universo de cada variable.** Muchas variables tienen filtros (por ejemplo, `pago_mensual_internet` solo aplica si `acceso_internet_hogar == "Sí"`). Documentar el universo evita reportar porcentajes calculados sobre la muestra total cuando deberían ser sobre el subgrupo correspondiente.

**Decidir si los descriptivos serán ponderados o no.** Para el informe oficial deben usarse los factores de expansión (`fe_personas` o `fe_hogar`). Para análisis exploratorio interno suele bastar con los datos sin ponderar. La recomendación es generar **ambas versiones** y reportar la ponderada en el documento final.

---

## 1. Inventario y clasificación de variables

Antes de describir, conviene producir un **inventario** que clasifique cada variable por tipo. Esto se hace una sola vez y luego sirve de mapa para todo el análisis.

```python
inventario = pd.DataFrame({
    "variable": df.columns,
    "tipo_pandas": df.dtypes.astype(str).values,
    "n_unicos": [df[c].nunique(dropna=True) for c in df.columns],
    "n_faltantes": df.isna().sum().values,
    "pct_faltantes": (df.isna().mean() * 100).round(1).values,
})
```

A partir del inventario, clasifica cada variable en una de estas categorías:

- **Identificadora** (id, fecha_fin) — no se describe estadísticamente.
- **Categórica nominal** (region, sexo, tipo_acceso_fijo, ocupacion).
- **Categórica ordinal** (gse, tramo_edad, nivel_habilidades, frecuencia_internet, percepcion_proteccion).
- **Binaria 0/1** (Q8_*, Q6_*, indicadores derivados).
- **Numérica discreta / conteos** (n_smartphones_hogar, n_computadores_hogar, n_actividades, n_dispositivos).
- **Numérica continua** (edad, pago_mensual_internet, pago_mensual_movil, ingreso_pm, fe_hogar, fe_personas).

El producto de esta etapa es una columna nueva en el inventario (`tipo_analisis`) que se usará para automatizar los descriptivos.

---

## 2. Análisis por tipo de variable

Cada tipo requiere estadísticos y visualizaciones distintas. La idea es estandarizar el procedimiento para cada tipo y aplicarlo en bucle.

### 2.1 Categóricas nominales

**Estadísticos:**
- Tabla de frecuencias absolutas y relativas (con y sin NaN).
- Moda y porcentaje de la moda.
- Número de categorías efectivas.

```python
def describir_nominal(serie):
    n = serie.notna().sum()
    freq = serie.value_counts(dropna=False)
    pct = (serie.value_counts(normalize=True, dropna=False) * 100).round(2)
    return pd.DataFrame({"n": freq, "pct": pct})
```

**Visualización:**
- Gráfico de barras horizontal ordenado por frecuencia (mejor que vertical cuando las etiquetas son largas, como en `region` o `ocupacion`).
- Para variables con muchas categorías (10+), considerar agrupar las menos frecuentes en "Otros".

**Variables prioritarias:** `region`, `comuna`, `zona`, `sexo`, `educ`, `educ_jh`, `ocupacion_encuestado`, `ocupacion_jh`, `tipo_acceso_fijo`, `tipo_plan`, `tipo_acceso_mas_usado`, `velocidad_contratada`.

### 2.2 Categóricas ordinales

Mismo tratamiento que las nominales, pero con consideraciones adicionales:

**Estadísticos adicionales:**
- Mediana (la categoría central acumulada al 50%).
- Distribución acumulada (cuántas personas están "en o bajo" cada nivel).

**Visualización:**
- Gráfico de barras **respetando el orden lógico** de las categorías (no ordenar por frecuencia).
- Útil agregar la línea acumulada si interesa ver dónde se concentra la masa.

```python
orden_gse = ["AB", "C1", "C2", "C3", "D", "E"]
df["gse"] = pd.Categorical(df["gse"], categories=orden_gse, ordered=True)
df["gse"].value_counts().reindex(orden_gse).plot.bar()
```

**Variables prioritarias:** `gse`, `educ_grupo`, `tramo_edad`, `ingreso_grupo`, `ingreso_tramo`, `nivel_habilidades`, `frecuencia_internet`, `tiempo_diario_internet`, `ultimo_uso_internet`, `percepcion_proteccion`.

### 2.3 Numéricas continuas

**Estadísticos:**
- Tendencia central: media, mediana, moda (si aplica).
- Dispersión: desviación estándar, rango intercuartílico, rango (mín–máx), coeficiente de variación.
- Forma: asimetría (skewness) y curtosis.
- Cuartiles y percentiles relevantes (p10, p25, p50, p75, p90, p95).

```python
df["pago_mensual_internet"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95])
df["pago_mensual_internet"].agg(["skew", "kurt"])
```

**Visualización:**
- **Histograma** con número de bins razonable (regla de Sturges o Freedman-Diaconis).
- **Boxplot** o violinplot para ver distribución y atípicos.
- **Q-Q plot** si interesa evaluar normalidad antes de aplicar pruebas paramétricas en etapas siguientes.

**Decisiones que hay que tomar:**
- Si la distribución es muy asimétrica (caso típico: `pago_mensual_internet`, `ingreso_pm`), reportar la **mediana** como medida principal en vez de la media, y considerar transformación logarítmica si después se usará en regresión.
- Definir el tratamiento de **valores atípicos** antes de pasar a etapas siguientes (ver sección 5).

**Variables prioritarias:** `edad`, `pago_mensual_internet`, `pago_mensual_movil`, `ingreso_pm`, `ingreso_hogar`, `freq_num`, `horas_num`.

### 2.4 Numéricas discretas (conteos)

**Estadísticos:**
- Mismos que continuas, pero la **mediana** y la **moda** suelen ser más informativas que la media.
- Distribución de frecuencias por valor (como una categórica), porque suelen tener pocos valores únicos.

**Visualización:**
- Histograma con bins de ancho 1, o gráfico de barras si hay menos de 15 valores únicos.

**Variables prioritarias:** `n_smartphones_hogar`, `n_computadores_hogar`, `n_actividades`, `n_dispositivos`, `intensidad_uso`.

### 2.5 Binarias 0/1

Estas son la mayoría de las variables del dataset (Q8_*, Q6_*, P3_*, etc.). Se describen como categóricas, pero como hay tantas conviene un tratamiento agregado.

**Estadísticos:**
- Prevalencia: proporción de "Sí" (o de 1).
- Número de respuestas válidas.

**Visualización:**
- Gráfico de barras horizontal con todas las variables del mismo bloque temático ordenadas por prevalencia. Por ejemplo, las 19 habilidades digitales (`Q8_1` a `Q8_19`) en un solo gráfico ordenado descendente da inmediatamente un mapa de qué habilidades son más y menos comunes.

```python
hab_cols = [c for c in df.columns if c.startswith("Q8_")]
prevalencias = df[hab_cols].mean().sort_values(ascending=False) * 100
prevalencias.plot.barh()
```

**Bloques de binarias a describir agregadamente:**
- Habilidades digitales (`Q8_*`, 19 variables).
- Actividades online (`Q21_*`, ~48 variables).
- Bienes del hogar (`A12_*`, `A13_*`, `A14_*`).
- Tipos de uso de smartphone (`Q11_1_*`).
- Razones de no acceso, lugares de uso, motivos, etc.

---

## 3. Organización por dominio temático

Además de organizar por tipo, conviene presentar los descriptivos siguiendo la lógica del cuestionario y del informe final. Los bloques temáticos sugeridos son:

**Bloque 1 — Caracterización del hogar y la persona**
- Geografía (region, zona, comuna).
- Sociodemografía individual (edad, tramo_edad, sexo, educ, educ_grupo, ocupacion_encuestado).
- Jefe de hogar (educ_jh, ocupacion_jh).
- Socioeconómico (gse, ingreso_pm, ingreso_grupo, ingreso_tramo).

**Bloque 2 — Equipamiento y acceso**
- Acceso a internet en el hogar (acceso_internet_hogar).
- Tipo de tecnología (tipo_acceso_fijo, tipo_plan).
- Características del servicio (pago_mensual_internet, velocidad_contratada, calidad_acceso).
- Equipamiento (n_smartphones_hogar, n_computadores_hogar, otros dispositivos).

**Bloque 3 — Uso individual**
- Uso de dispositivos (uso_computador, uso_smartphone, smartphone_propio).
- Uso de internet (ultimo_uso_internet, frecuencia_internet, tiempo_diario_internet, tipo_acceso_mas_usado).
- Plan móvil (plan_movil_tipo_ind, pago_mensual_movil).
- Lugares de uso (Q11_1_*).

**Bloque 4 — Habilidades digitales**
- Nivel agregado (nivel_habilidades).
- Habilidades específicas (Q8_1 a Q8_19).
- Categorías derivadas (cat_ofimatica, cat_rrss_y_comunicacion, cat_seguridad, etc.).

**Bloque 5 — Actividades online**
- Actividades realizadas (Q21_1 a Q21_48).
- Compras online (ultima_compra_online, Q28_*).
- Indicadores derivados (n_actividades, intensidad_uso).

**Bloque 6 — Percepciones y regulación**
- Percepciones generales (internet_facilita_trabajo, internet_mejora_vida).
- Protección y seguridad (percepcion_proteccion, reg_*).
- Brechas percibidas (Q34_*, Q37_*, Q38_*).

Para cada bloque, generar una **ficha temática** de 1–2 páginas con los principales estadísticos y visualizaciones. Esto facilita la redacción del informe.

---

## 4. Análisis de datos faltantes

Es parte esencial del descriptivo univariado y suele omitirse. Tres niveles:

**4.1 Faltantes por variable.** Ya está en el inventario (`pct_faltantes`). Identificar:
- Variables con faltantes > 50% (probablemente filtradas o con problemas).
- Variables con faltantes inesperados (universo total que debería tener 0%).

**4.2 Faltantes por caso.** Cuántas variables responde cada persona en promedio. Detecta entrevistas incompletas o problemas de recolección.

```python
df["n_faltantes_caso"] = df.isna().sum(axis=1)
df["n_faltantes_caso"].describe()
```

**4.3 Patrón de faltantes.** Visualización con `missingno` para ver si los faltantes son aleatorios o estructurados (por ejemplo, todos los que no tienen acceso a internet faltan en las preguntas de uso).

```python
import missingno as msno
msno.matrix(df[variables_clave])
msno.heatmap(df[variables_clave])
```

---

## 5. Detección de valores atípicos

Para variables numéricas, identificar y caracterizar los outliers antes de continuar.

**Método 1 — Regla de Tukey (IQR):** valores fuera de [Q1 − 1.5·IQR, Q3 + 1.5·IQR].

**Método 2 — Z-score:** valores con |z| > 3.

**Método 3 — Reglas de dominio:** algunos valores son sustantivamente imposibles o sospechosos (por ejemplo, `pago_mensual_internet` mayor a $300.000, `n_smartphones_hogar > 10`).

Documentar:
- Cuántos casos atípicos por variable.
- Si se mantienen, se recortan (winsorize) o se tratan como missing.
- La decisión debe quedar explícita y replicable.

---

## 6. Estadísticos ponderados

Para todos los estadísticos del informe oficial, repetir el cálculo aplicando los factores de expansión.

**Para proporciones (categóricas y binarias):**

```python
def freq_ponderada(df, var, peso="fe_personas"):
    return df.groupby(var)[peso].sum() / df[peso].sum() * 100
```

**Para medias y medianas (numéricas):**

```python
import numpy as np
def media_ponderada(df, var, peso="fe_personas"):
    valido = df[var].notna()
    return np.average(df.loc[valido, var], weights=df.loc[valido, peso])

# Mediana ponderada con statsmodels
from statsmodels.stats.weightstats import DescrStatsW
d = DescrStatsW(df[var].dropna(), weights=df.loc[df[var].notna(), peso])
d.quantile([0.5])
```

**Regla práctica:** usar `fe_personas` para variables individuales (uso, habilidades, percepciones) y `fe_hogar` para variables del hogar (acceso, equipamiento, pago).

---

## 7. Productos esperados

Al finalizar esta etapa debes tener:

1. **Notebook `00_descriptivo_univariado.ipynb`** — código reproducible que genera todos los descriptivos.
2. **Inventario de variables clasificadas** — exportado como CSV (`data/derivados/inventario_variables.csv`).
3. **Tabla maestra de descriptivos** — un CSV por tipo de variable con los estadísticos clave (`data/derivados/descriptivos_categoricas.csv`, etc.).
4. **Galería de gráficos** — carpeta `figuras/univariado/` con un gráfico por variable o bloque, en formato PNG y/o SVG.
5. **Ficha temática por bloque** — 6 archivos resumen (uno por dominio) con los hallazgos principales en lenguaje natural.
6. **Reporte de calidad de datos** — documento corto que liste variables con problemas (faltantes excesivos, atípicos, valores fuera de rango) y la decisión tomada para cada una.

---

## 8. Cronograma sugerido

| Etapa | Tiempo estimado |
|---|---|
| Preparación e inventario | 1–2 días |
| Descriptivos por tipo (secciones 2.1 a 2.5) | 3–5 días |
| Organización temática y fichas | 3–5 días |
| Análisis de faltantes y atípicos | 2 días |
| Versiones ponderadas y validación | 2 días |
| **Total** | **2–3 semanas** |

---

## 9. Recomendación de flujo

Dado que algunas tareas son repetitivas (mismo procedimiento para muchas variables), conviene:

1. Escribir **funciones reutilizables** para cada tipo de variable (`describir_nominal`, `describir_ordinal`, `describir_continua`, `describir_binaria`).
2. Iterar sobre el inventario aplicando la función correspondiente según `tipo_analisis`.
3. Guardar los resultados en estructuras estandarizadas (un DataFrame por tipo) que después se puedan consultar y exportar.
4. Generar los gráficos también en bucle, con nombres de archivo basados en el nombre de la variable.

Esto evita escribir código repetitivo para cientos de variables y garantiza que todas reciban el mismo tratamiento.
