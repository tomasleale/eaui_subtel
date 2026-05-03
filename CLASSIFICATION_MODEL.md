# Modelo de Clasificación: Predicción de Habilidades Digitales

**Objetivo:** Predecir `nivel_habilidades` (Avanzado, Intermedio, Básico, Sin habilidades)  
**Dataset:** 4,218 personas con complete cases  
**Features:** 7 variables (edad, GSE, educación, zona, sexo, ingreso, acceso internet)  
**Target:** 4 clases desbalanceadas

---

## Distribución de Clases (Training Set)

| Clase | N | % |
|-------|---|---|
| Intermedio | 1,877 | 44.5% |
| Avanzado | 1,351 | 32.0% |
| Básico | 636 | 15.1% |
| Sin habilidades | 354 | 8.4% |

**Desbalance:** Clase mayoritaria (Intermedio) es 5.3× la clase minoritaria (Sin habilidades).

---

## Modelos Entrenados

### 1. Random Forest (Baseline)

**Hiperparámetros:**
- n_estimators: 100
- max_depth: 15
- random_state: 42

**Desempeño:**
- Accuracy: 52.1%
- F1-Score: 0.5189 (weighted)

**Feature Importance:**
```
edad                 55.3%
educ_jh              16.2%
gse                  11.3%
ingreso_grupo         6.3%
sexo                  3.6%
zona                  3.6%
acceso_internet       3.6%
```

**Problema:** Sobrepredice "Intermedio" (la clase mayoritaria). Sesgo hacia la clase dominante.

---

### 2. Logistic Regression (Baseline Lineal)

**Hiperparámetros:**
- max_iter: 1,000
- Scaling: StandardScaler

**Desempeño:**
- Accuracy: 56.9% ⬆️
- F1-Score: 0.5653 (weighted)

**Mejora sobre RF:** +4.8 puntos de accuracy

**Por clase:**
| Clase | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| Avanzado | 0.62 | 0.57 | 0.59 |
| Intermedio | 0.55 | 0.65 | 0.60 |
| Básico | 0.47 | 0.46 | 0.47 |
| Sin habilidades | **0.85** | **0.32** | 0.47 |

**Insight:** LR es muy preciso al predecir "Sin habilidades" (85%) pero falla en recall (32%). Identifica correctamente cuando alguien NO tiene skills, pero se pierde muchos casos.

---

### 3. Gradient Boosting ⭐ (Mejor)

**Hiperparámetros:**
- n_estimators: 100
- max_depth: 5
- random_state: 42

**Desempeño:**
- Accuracy: **57.2%** 🏆
- F1-Score: **0.5695** (weighted)

**Mejora sobre RF:** +5.1 puntos | Sobre LR: +0.3 puntos

**Por clase:**
| Clase | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| Avanzado | 0.60 | 0.60 | **0.60** |
| Intermedio | 0.57 | 0.63 | **0.60** |
| Básico | 0.48 | 0.40 | 0.44 |
| Sin habilidades | 0.62 | 0.46 | 0.53 |

**Ventaja:** Mejor balance entre precision/recall. No sobrepredice clases mayoritarias.

**Feature Importance:**
```
edad                 46.4%
gse                  17.2%
educ_jh              15.1%
acceso_internet       8.2%
ingreso_grupo         6.1%
sexo                  4.0%
zona                  3.0%
```

---

## Comparativa Resumida

```
ACCURACY (Test Set)
├─ Gradient Boosting:    ██████████████████ 57.2%
├─ Logistic Regression:  █████████████████  56.9%
└─ Random Forest:        ███████████████    52.1%

F1-SCORE (Weighted)
├─ Gradient Boosting:    0.5695
├─ Logistic Regression:  0.5653
└─ Random Forest:        0.5189
```

---

## Feature Importance Analysis

### Edad Domina (46.4% en GB)

**Por qué es el predictor más fuerte:**
- Jóvenes (18-29) alcanzan skills más rápido
- Adultos mayores (60+) menos exposición
- Efecto cohorte: digital natives vs análogos

**Implicación:** Edad es más predictiva que recursos económicos. Una persona joven en pobreza tiene más chances de aprender skills que un adulto rico sin exposición.

---

### GSE + Educación (32% combinado)

**GSE (17.2%):** Proxy de recursos (dinero, dispositivos, internet)

**Educación (15.1%):** Proxy de capital humano y modelaje parental

**Relación no-aditiva:** Alguien pobre pero joven con educación media supera a alguien rico pero viejo sin educación.

---

### Acceso Internet (8.2%)

**Inferior a lo esperado.** Hipótesis:
- Dataset ya filtrado a gente con internet (78.8% tiene acceso)
- Entre quienes tienen acceso, la variación en skills viene de edad/educación, no del acceso per se

**Reinterpretar:** Acceso es **binario gate** (80% sin internet = sin skills), pero entre conectados, edad >> acceso.

---

### Zona, Sexo (3-4%)

Casi irrelevantes en el modelo. El efecto rural se captura ya en GSE (hogares rurales tienden a ser más pobres).

---

## Análisis de Errores

### Confusión más frecuente: Intermedio ↔ Avanzado

**RF:** 118 de 270 "Avanzado" predichos como "Intermedio"  
**Causa:** Frontera difusa entre niveles. Una persona que domina Excel (Intermedio) pero no programación podría declararse a sí misma como "Avanzado" sin serlo.

### Clase difícil: Básico

- **Recall:** 40% en GB (pierdo 60% de casos reales)
- **Precision:** 48% (cuando predigo Básico, aciertan apenas 48% de veces)
- **Causa:** Overlap con Intermedio. Personas que usan social media + email podrían estar en ambas categorías.

### Sin habilidades (clase rara)

- 8.4% de la población
- Muy predecible si no tiene internet (79.6%)
- Pero entre conectados, es el 4-5% más problemático

---

## Limitaciones del Modelo

### 1. **Desbalance de Clases**
Intermedio es 5.3× Sin habilidades. El modelo aprende patrones del 44.5% de datos (Intermedio) más que del 8.4% raro (Sin habilidades).

**Posible solución:** Class weighting o SMOTE (synthetic oversampling).

### 2. **Feature Engineering Limitado**
Usamos solo 7 features "macro" (edad, GSE, educación). Faltan:
- # de dispositivos (P2, P2_1)
- Frecuencia de uso (Q10, Q11)
- Tipos de actividades (Q21_*, Q28_*)
- Exposición en el trabajo (Q23, Q25)

Estos podrían subir accuracy a 65-70%.

### 3. **Autocorrelación en Features**
- `educ_jh` → en parte → `gse`
- `edad` + `gse` están correlacionadas (GSE mejora con cohorte)
- Multicolinealidad moderada

**Impacto:** Feature importance puede ser sesgada. El efecto de edad puede estar capturando cambio generacional en GSE.

### 4. **Definición borrosa de Clases**
`nivel_habilidades` es jerárquico pero threshold entre Básico/Intermedio es ambiguo:
- Básico: mínimo 1 de {email, videollamadas, redes}
- Intermedio: mínimo 1 de {Word, Excel, PowerPoint}

¿Una persona que domina Excel pero no sabe enviar emails en qué clase cae? La respuesta depende del orden de evaluación.

---

## Recomendaciones para Deployment

### 1. **Usar Gradient Boosting**
57.2% accuracy es suficiente para segmentación exploratoria, no para decisiones críticas.

```python
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=100, max_depth=5, 
    learning_rate=0.1, random_state=42
)
model.fit(X_train, y_train)
y_pred = model.predict(X_new)
y_proba = model.predict_proba(X_new)  # confianza
```

### 2. **Usar Probabilidades, No Predicciones**
57% accuracy ≠ 57% confianza. Usar `predict_proba()`:

```python
# En lugar de:
nivel = model.predict(X)[0]  # "Intermedio"

# Hacer:
probs = model.predict_proba(X)[0]  # [0.35, 0.48, 0.12, 0.05]
if max(probs) < 0.40:
    return "Incierto - requiere confirmación humana"
```

### 3. **Aplicar a Segmentación, No Predicción Individual**
El modelo es mejor para segmentar poblaciones (¿cuál % de rural+bajo+joven es Avanzado?) que predecir a una persona específica.

### 4. **Reentrenar Anualmente**
Cohortes más jóvenes tienen skills diferentes. El modelo de 2026 no vale para 2030.

### 5. **Agregar Features**
Para production, incluir:
- `Q21_*` (actividades online: redes, email, transacciones)
- `Q10` (frecuencia de uso)
- `P2` (# dispositivos en hogar)
- Interacciones: `edad × gse`, `acceso_internet × educ_jh`

---

## Archivos Generados

- `CLASSIFICATION_MODEL.md` — Este documento
- Modelo guardado: `models/nivel_habilidades_gb.pkl` (si se guarda)
- Feature importance plot: `plots/feature_importance.png` (si se genera)

---

## Conclusión

**Las habilidades digitales SÍ se pueden predecir** con ~57% accuracy usando variables socioeconómicas y demográficas básicas.

**El factor más fuerte es la edad**, seguido por GSE y educación. Esto valida hallazgos de la resilience analysis: **jóvenes de familias pobres pueden superar barreras de ingresos a través de exposición y aprendizaje temprano.**

El modelo no es perfecto (Básico es difícil, hay overfitting a Intermedio), pero es **útil para diseño de políticas**: identificar qué grupos necesitan intervención prioritaria.

**Siguiente paso:** Agregar features ricas (actividades online, dispositivos, frecuencia de uso) para subir accuracy a 70%.
