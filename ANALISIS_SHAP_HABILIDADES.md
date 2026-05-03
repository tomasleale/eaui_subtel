# Análisis SHAP - Modelo de Predicción de Nivel de Habilidades Digitales

## Resumen Ejecutivo

Este documento sintetiza el análisis SHAP (SHapley Additive exPlanations) de un modelo Random Forest entrenado para predecir el Nivel de Habilidades Digitales (Avanzado, Intermedio, Básico, Sin habilidades) usando datos de acceso y uso de internet de la encuesta EAUI 2026.

### Métricas Clave

| Métrica | Valor |
|---------|-------|
| **Precisión del Modelo** | 61.5% (1,000 muestras de prueba) |
| **Total de Registros** | 5,000 |
| **Features Utilizados** | 9 (6 numéricos + 3 categóricos) |
| **Clases Objetivo** | 4 (Avanzado, Básico, Intermedio, Sin habilidades) |
| **Método SHAP** | TreeExplainer con indexación multiclass (n_samples, n_features, n_classes) |
| **Clases Balanceadas** | Sí (class_weight='balanced') |

## Datos y Preparación

### Distribución de Variable Objetivo (Nivel de Habilidades)

```
Intermedio        → 2,226 registros  (44.5%) ← Mayoritaria
Avanzado          → 1,548 registros  (30.9%)
Básico            →   805 registros  (16.1%)
Sin habilidades   →   421 registros  (8.4%)
```

### Split de Datos

- **Entrenamiento:** 4,000 registros (80%)
- **Prueba:** 1,000 registros (20%)
- **Normalización:** StandardScaler (media=0, std=1)
- **Codificación:** LabelEncoder para features categóricos

### Cálculo de Nivel de Habilidades

Basado en respuestas a preguntas de habilidades Q8 del cuestionario:

- **Avanzado:** Si responde positivo (=1) a cualquier de {Q8_7, Q8_8, Q8_9}
- **Intermedio:** Si responde positivo a cualquiera de {Q8_1 a Q8_6, Q8_14, Q8_17, Q8_18}
- **Básico:** Si responde positivo a cualquiera de {Q8_10 a Q8_13, Q8_15, Q8_16}
- **Sin habilidades:** Ninguna respuesta positiva

## Features Utilizados

### Numéricos (6)

| Feature | Descripción | Rango |
|---------|-------------|-------|
| `edad` | Edad del entrevistado en años | 18-75+ |
| `n_disp` | Cantidad de dispositivos disponibles | 0-8 |
| `n_act` | Número de actividades online realizadas | 0-41 |
| `intens` | Índice combinado frecuencia × horas diarias | 0-20 |
| `pago_int` | Gasto mensual en internet fijo (CLP) | 0-999,999 |
| `pago_mov` | Gasto mensual en móvil/datos (CLP) | 0-999,999 |

### Categóricos (3)

| Feature | Categorías | Codificación |
|---------|-----------|--------------|
| `sexo` | Hombre (H), Mujer (M) | 0/1 |
| `zona` | Rural (R), Urbana (U) | 0/1 |
| `uso_sp` | No smartphone (0), Sí smartphone (1) | 0/1 |

## Resultados SHAP: Top Features por Importancia

### Ranking Completo de Features por Impacto SHAP

| Rank | Feature | SHAP Value | Interpretación |
|------|---------|-----------|----------------|
| 1 | **n_act** | 0.0770 | Actividades online más impactantes que edad |
| 2 | **edad** | 0.0610 | Edad sigue siendo importante predictor |
| 3 | **intens** | 0.0499 | Intensidad de uso diferencia habilidades |
| 4 | **n_disp** | 0.0377 | Múltiples dispositivos indican mayor habilidad |
| 5 | **uso_spe** | 0.0376 | Uso de smartphone correlaciona con habilidades |
| 6 | **pago_mov** | 0.0319 | Gasto en móvil indica capacidad/necesidad |
| 7 | **pago_int** | 0.0248 | Gasto en internet menos impactante que móvil |
| 8 | **sexoe** | 0.0209 | Género con impacto menor |
| 9 | **zonae** | 0.0103 | Ubicación (rural/urbana) menos relevante |

### Hallazgos Principales

#### 1. **Actividades Online es el Factor Dominante** ✓
- **SHAP: 0.0770** (mayor impacto)
- Feature Importance (RF): 0.131 (tercero)
- **Interpretación:** La DIVERSIDAD de actividades online es más importante para predecir habilidad que la demografía
- Personas que hacen más tipos de actividades tienen mayor nivel de habilidades

#### 2. **Edad Sigue Siendo Importante** ✓
- **SHAP: 0.0610** (segundo mayor)
- Feature Importance (RF): 0.222 (primero)
- **Interpretación:** Hay gap entre RF y SHAP: RF confía mucho en edad para dividir árboles, pero el impacto real es menor
- Sugiere edad actúa como proxy para otras variables

#### 3. **Intensidad de Uso Diferencia Grupos** ✓
- **SHAP: 0.0499**
- Feature Importance (RF): 0.118
- **Interpretación:** Cuánto tiempo dedica (no solo acceso) correlaciona con habilidades
- Grupos de mayor habilidad dedican más horas

#### 4. **Dispositivos Múltiples son Indicador** ✓
- **SHAP: 0.0377**
- Feature Importance (RF): 0.093
- **Interpretación:** Tener smartphone + computadora + tablet → nivel más alto
- Refleja capacidad de inversión y necesidad de dispositivos

#### 5. **Zona Geográfica es Menos Relevante** ✗
- **SHAP: 0.0103** (menor impacto)
- Feature Importance (RF): (no aparece en top 8)
- **Interpretación:** Rural/Urbana no diferencia habilidades tanto como otros factores
- Sugerencia: Enfocarse en variables de acceso, no ubicación

## Comparación: SHAP vs Feature Importance Tradicional

```
Feature         | RF Importance | SHAP  | Diferencia
─────────────────────────────────────────────────────
edad            | 0.222         | 0.061 | RF > SHAP (RF confía más)
pago_mov        | 0.157         | 0.032 | RF > SHAP 
n_act           | 0.131         | 0.077 | RF < SHAP (SHAP más importante)
intens          | 0.118         | 0.050 | RF > SHAP
uso_spe         | 0.116         | 0.038 | RF > SHAP
pago_int        | 0.111         | 0.025 | RF > SHAP
n_disp          | 0.093         | 0.038 | RF > SHAP
sexoe           | 0.027         | 0.021 | RF ≈ SHAP
```

### Interpretación de Diferencias

- **RF confía en edad:** Usa edad para dividir árboles (impureza), pero el impacto real en predicción es menor
- **SHAP prioriza actividades:** Las actividades impactan más el valor final de la predicción
- **Validación cruzada sugerida:** Las dos métricas tienen visiones complementarias

## Desempeño del Modelo

### Métricas Generales

- **Accuracy Global:** 61.5% (1,000 muestras)
- **Macro Avg F1-Score:** 0.63
- **Weighted Avg F1-Score:** 0.62

### Por Clase

| Clase | Precisión | Recall | F1-Score | Soporte |
|-------|-----------|--------|----------|---------|
| Avanzado | 0.66 | 0.58 | 0.62 | 310 |
| Básico | 0.53 | 0.50 | 0.51 | 161 |
| Intermedio | 0.58 | 0.66 | 0.62 | 445 |
| Sin habilidades | 0.86 | 0.70 | 0.77 | 84 |

### Interpretación de Clases

- **Sin habilidades:** Mejor predicción (F1=0.77) - es bien diferenciable
- **Avanzado:** Predicción buena (F1=0.62) - características claras
- **Intermedio:** Recall alto (0.66) pero precisión moderada - clase heterogénea
- **Básico:** Peor predicción (F1=0.51) - sobrelapamiento con otras clases

## Implicaciones para Políticas y Programas

### 1. Estimular Diversidad de Actividades Online
- **Hallazgo:** n_act es el predictor SHAP más fuerte
- **Acción:** Programas que exponen usuarios a diferentes tipos de actividades (trabajo, ocio, redes, compras, etc.)
- **Beneficio:** Aumentar habilidades digitales mediante práctica diversa

### 2. Enfoque Diferenciado por Grupo de Edad
- **Hallazgo:** Edad importante pero con matices
- **Acción:** Capacitación adaptada a cohortes de edad (no asumir habilidades por edad)
- **Beneficio:** Mejor targeting de programas

### 3. Intensidad de Uso es Relevante
- **Hallazgo:** intens SHAP=0.050
- **Acción:** Incentivar mayor dedicación de tiempo a internet (especialmente en grupos básicos)
- **Beneficio:** Más práctica = mejores habilidades

### 4. Acceso a Múltiples Dispositivos Importa
- **Hallazgo:** n_disp SHAP=0.038
- **Acción:** Programas de subsidy para segundos/terceros dispositivos
- **Beneficio:** Multiplicar oportunidades de práctica

## Robustez y Reproducibilidad

### ✓ Medidas Implementadas

- **Random state fijo (42):** Garantiza reproducibilidad exacta
- **Imputación robusta:** Mediana para numéricos, moda para categóricos
- **StandardScaler:** Normalización consistente
- **LabelEncoders:** Codificación reversible
- **Class weighting:** Manejo de desbalance de clases
- **Multiclass indexing correcto:** TreeExplainer shape (n_samples, n_features, n_classes)

### Cómo Ejecutar Nuevamente

```bash
# Asegurar que el entorno datascience está activo
cd /Users/tomas/github/eaui_subtel

# Ejecutar notebook completo
jupyter nbconvert --to notebook --execute eaui2026_v5.ipynb --output eaui2026_v5_executed.ipynb
```

### Validación de Datos

| Archivo Requerido | Ubicación | Validación |
|------------------|-----------|-----------|
| Datos SPSS 2026 | `/data/sav/2026.sav` | 5,000 registros × 587 variables |
| Notebook | `/eaui2026_v5.ipynb` | 8 celdas completas |
| Entorno Python | `datascience` | pyenv-virtualenv activo |

## Próximos Pasos Recomendados

### 1. Análisis de Interacciones SHAP
- Crear interaction plots para ver cómo n_act y edad interactúan
- Ejemplo: ¿La importancia de n_act es diferente para edades distintas?

### 2. Validación Cruzada de Modelos
- Comparar con GradientBoosting, XGBoost
- Ver si importancias SHAP se mantienen consistentes

### 3. Predicciones Individuales
- Usar SHAP para explicar por qué un usuario específico fue clasificado en cierto nivel
- Generar "cartas de explicación" para programas de capacitación

### 4. Segmentación Posterior
- Analizar SHAP por subgrupos (rural vs urbana, hombre vs mujer)
- Validar si importancias cambian por demografía

## Archivos Generados

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `eaui2026_v5.ipynb` | Jupyter | Notebook ejecutable completo |
| `eaui2026_v5_executed.ipynb` | Jupyter | Notebook con resultados ejecutados |
| `shap_ranking_habilidades.csv` | CSV | Ranking completo de features SHAP |
| `ANALISIS_SHAP_HABILIDADES.md` | Markdown | Este documento |

## Conclusión

El análisis SHAP ha identificado que **actividades online, edad e intensidad de uso** son los factores con mayor impacto en la predicción de nivel de habilidades digitales. Con una precisión de 61.5%, el modelo proporciona insights valiosos sobre QUÉ factores correlacionan más fuertemente con habilidades digitales autoreportadas, aunque hay heterogeneidad dentro de clases que sugiere que las habilidades digitales son multidimensionales.

---

**Generado:** 2026-05-03  
**Versión:** 1.0  
**Autor:** Claude Code - Análisis SHAP Automatizado  
**Dataset:** EAUI 2026 SUBTEL (5,000 registros)
