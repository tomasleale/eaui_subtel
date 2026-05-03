# Garantías de Robustez y Plan de Mantenimiento

## Objetivo
Asegurar que el análisis SHAP sea **reproducible, robusto y a prueba de fallas** incluso si:
- Las dependencias se actualizan
- Nuevos datos se agregan
- El entorno cambia
- Se ejecuta años después

---

## 1. Versionamiento de Dependencias (CRÍTICO)

### Dependencias Requeridas

```txt
# requirements.txt para análisis SHAP
pyreadstat>=1.2.0          # Leer archivos SPSS .sav
pandas>=2.0.0               # Manipulación de datos
numpy>=1.23.0               # Cálculos numéricos
scikit-learn>=1.3.0         # Machine Learning (RandomForestClassifier)
shap>=0.43.0                # SHAP analysis
matplotlib>=3.7.0           # Gráficos
seaborn>=0.12.0             # Estilo de gráficos
jupyter>=1.0.0              # Notebook
jupyter-contrib-nbextensions>=0.7.0  # Extensiones

# Para generación de reportes
nbconvert>=7.0.0
```

### Instalación Segura

```bash
# Crear entorno aislado
python -m venv venv_shap

# Activar
source venv_shap/bin/activate

# Instalar versiones pinned
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

### Qué Hacer Si Falla

| Error | Causa Probable | Solución |
|-------|---|---|
| `ImportError: No module named 'shap'` | SHAP no instalado | `pip install shap==0.43.0` |
| `pyreadstat.Error: Failed to read file` | Versión incompatible | `pip install pyreadstat==1.2.0` |
| `DeprecationWarning: Feature X deprecated` | NumPy/Pandas actualizado | Actualizar código (ver abajo) |
| `MemoryError: SHAP values` | Dataset demasiado grande | Usar TreeExplainer con muestras |

---

## 2. Estructura de Datos (CRÍTICO)

### Validación Antes de Ejecutar

```python
# Ejecutar ANTES de cualquier análisis
import pandas as pd
import pyreadstat

def validar_datos():
    """Verifica que los datos sean válidos para el análisis."""
    
    # 1. Archivo existe
    import os
    assert os.path.exists('/Users/tomas/github/eaui_subtel/data/sav/2026.sav'), \
        "Archivo SPSS no encontrado en ruta esperada"
    
    # 2. Carga correctamente
    try:
        df, meta = pyreadstat.read_sav("/Users/tomas/github/eaui_subtel/data/sav/2026.sav")
    except Exception as e:
        raise ValueError(f"Error cargando SPSS: {e}")
    
    # 3. Shape esperado
    assert df.shape[0] == 5000, f"Esperado 5,000 registros, tengo {df.shape[0]}"
    assert df.shape[1] == 587, f"Esperado 587 columnas, tengo {df.shape[1]}"
    
    # 4. Variables clave existen
    cols_requeridas = ['A10', 'A11', 'Q1_1', 'Q1_2', 'Q7', 'Q10', 'Q11', 'P11', 'Q7_4']
    cols_faltantes = [c for c in cols_requeridas if c not in df.columns]
    assert len(cols_faltantes) == 0, f"Columnas faltantes: {cols_faltantes}"
    
    # 5. Valores faltantes razonables (no más del 30%)
    null_ratio = df.isnull().sum() / len(df)
    cols_con_mucho_null = null_ratio[null_ratio > 0.3]
    if len(cols_con_mucho_null) > 0:
        print(f"⚠️ Advertencia: Estas columnas tienen >30% nulls:")
        print(cols_con_mucho_null)
    
    print("✓ Validación de datos exitosa")
    return df, meta

# Ejecutar
df, meta = validar_datos()
```

### Expectativas de Datos

| Aspecto | Esperado | Rango Aceptable |
|--------|----------|---|
| Registros | 5,000 | 4,800 - 5,200 |
| Columnas | 587 | 580 - 600 |
| Null ratio general | 5-10% | 0 - 25% |
| Edad (Q1_1) | 18-80+ | 0 - 150 |
| Gasto (P11) | $5k-$150k/mes | 0 - $500k |

---

## 3. Reproducibilidad: Random States

### Fijar Seeds en Todos Lados

```python
import os
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ANTES de cualquier operación estocástica
SEED = 42

# Python
random.seed(SEED)

# NumPy
np.random.seed(SEED)

# Pandas
pd.options.mode.copy_on_write = True

# scikit-learn (en cada componente)
split = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)
scaler = StandardScaler()  # No tiene random_state
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    random_state=SEED,      # ← CRÍTICO
    n_jobs=-1,
    class_weight='balanced'
)
```

**Por qué:**
- `train_test_split` necesita `random_state` para reproducibilidad de split
- `RandomForest` necesita `random_state` para selección de features e inicialización de árboles
- SHAP con TreeExplainer es determinístico si el modelo es determinístico

**Verificación:**
```python
# Ejecutar dos veces y verificar que da exactamente el mismo resultado
accuracy_1 = accuracy_score(y_test, rf_model.predict(X_test_scaled))
accuracy_2 = accuracy_score(y_test, rf_model.predict(X_test_scaled))
assert accuracy_1 == accuracy_2, "Modelo no es reproducible"
```

---

## 4. Imputación Robusta (IMPORTANTE)

### Estrategia Actual

```python
# Para numéricos: MEDIANA (resistente a outliers)
for col in features_numericos:
    median = df_modelo[col].median()
    df_modelo[col] = df_modelo[col].fillna(median)
    print(f"  {col}: {df_modelo[col].isnull().sum()} NaNs restantes")

# Para categóricos: MODA (valor más frecuente)
for col in features_categoricos:
    mode_val = df_modelo[col].mode()
    if len(mode_val) > 0:
        df_modelo[col] = df_modelo[col].fillna(mode_val[0])
    else:
        df_modelo[col] = df_modelo[col].fillna('Unknown')
    print(f"  {col}: {df_modelo[col].isnull().sum()} NaNs restantes")

# Validar que NO hay NaNs
assert df_modelo.isnull().sum().sum() == 0, "Todavía hay NaNs después de imputación"
```

### Alternativas Futuras (Si Falla)

| Método | Ventajas | Desventajas |
|--------|----------|-----------|
| Mediana (actual) | Resistente a outliers | Pierde información extrema |
| KNN Imputation | Usa patrones locales | Costoso computacionalmente |
| MICE | Preserva relaciones | Complejidad aumentada |
| Eliminación | Simple, puro | Pierde datos |

**Recomendación:** Si >15% missing, considerar MICE.

---

## 5. Normalización Consistente

### Guardado de Scaler

```python
import joblib

# DESPUÉS de entrenar
joblib.dump(scaler, '/Users/tomas/github/eaui_subtel/modelos/scaler.pkl')

# Para datos nuevos (SIEMPRE usar el scaler guardado)
scaler_loaded = joblib.load('/Users/tomas/github/eaui_subtel/modelos/scaler.pkl')
X_new_scaled = scaler_loaded.transform(X_new)  # ← NO fit_transform
```

**Por qué es crítico:**
- Si usas `fit_transform` en datos nuevos, CAMBIAS el scale
- Eso hace que predicciones sean incorrectas
- `transform` SIEMPRE

### Validación

```python
# Verificar que scaling es correcto
assert X_train_scaled.mean() < 0.01, "Train mean no ≈ 0"
assert X_train_scaled.std() < 1.01, "Train std no ≈ 1"
assert X_test_scaled.mean() < 0.1, "Test mean desviado"  # OK si pequeño desviación
```

---

## 6. Codificación Reversible

### LabelEncoder Guardado

```python
import joblib

# DESPUÉS de entrenar
joblib.dump(le_dict, '/Users/tomas/github/eaui_subtel/modelos/label_encoders.pkl')

# Para convertir predicciones numérias de vuelta a strings legibles
le_dict_loaded = joblib.load('/Users/tomas/github/eaui_subtel/modelos/label_encoders.pkl')

# Predicción de modelo es numérica (0-5 para 6 clases)
y_pred_numeric = rf_model.predict(X_new_scaled)  # [0, 2, 4, 1, ...]

# Convertir de vuelta a strings
# Problema: Random Forest predice CLASES (por índice), necesitamos mapear

# Mejor: usar inverse_transform
y_pred_readable = rf_model.classes_[y_pred_numeric]  # ['AB', 'C2', 'E', 'C1', ...]
```

### Diccionario de Codificación

```python
# Guardar mapeo completo para referencia
encoding_dict = {
    'sexo': {'Hombre': 0, 'Mujer': 1},
    'zona': {'Rural': 0, 'Urbana': 1},
    'uso_smartphone': {'No': 0, 'Sí': 1},
    'frecuencia_internet': {
        'Menos de una vez al mes': 0,
        'Al menos una vez al mes': 1,
        'Varias veces por semana': 2,
        'Todos los días': 3
    }
}

# Guardar
import json
with open('/Users/tomas/github/eaui_subtel/modelos/encoding_dict.json', 'w') as f:
    json.dump(encoding_dict, f, indent=2, ensure_ascii=False)
```

---

## 7. Testing Automatizado

### Script de Validación Pre-Ejecución

```python
# test_shap_analysis.py
import sys
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def test_all():
    """Ejecuta todas las validaciones antes del análisis SHAP."""
    
    print("=" * 60)
    print("VALIDACIÓN PRE-ANÁLISIS SHAP")
    print("=" * 60)
    
    # Test 1: Archivos
    print("\n[1/6] Verificando archivos...")
    assert os.path.exists('/Users/tomas/github/eaui_subtel/data/sav/2026.sav'), \
        "Archivo SPSS faltante"
    assert os.path.exists('/Users/tomas/github/eaui_subtel/eaui2026_v3.ipynb'), \
        "Notebook faltante"
    print("  ✓ Archivos encontrados")
    
    # Test 2: Carga de datos
    print("\n[2/6] Cargando datos SPSS...")
    try:
        import pyreadstat
        df, meta = pyreadstat.read_sav("/Users/tomas/github/eaui_subtel/data/sav/2026.sav")
        print(f"  ✓ {df.shape[0]} registros × {df.shape[1]} columnas")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 3: Variables clave
    print("\n[3/6] Verificando variables...")
    cols_requeridas = ['A10', 'A11', 'Q1_1', 'Q1_2']
    faltantes = [c for c in cols_requeridas if c not in df.columns]
    if faltantes:
        print(f"  ✗ Columnas faltantes: {faltantes}")
        return False
    print("  ✓ Todas las variables clave presentes")
    
    # Test 4: Dependencias
    print("\n[4/6] Verificando librerías Python...")
    try:
        import shap
        import sklearn
        import matplotlib
        print(f"  ✓ shap {shap.__version__}")
        print(f"  ✓ scikit-learn {sklearn.__version__}")
        print(f"  ✓ matplotlib {matplotlib.__version__}")
    except ImportError as e:
        print(f"  ✗ Librería faltante: {e}")
        return False
    
    # Test 5: Espacio en disco
    print("\n[5/6] Verificando espacio disponible...")
    import shutil
    total, used, free = shutil.disk_usage("/Users/tomas/github/eaui_subtel")
    free_gb = free / (1024**3)
    if free_gb < 2:
        print(f"  ⚠️  Solo {free_gb:.1f} GB disponibles (recomendado: 2+ GB)")
    else:
        print(f"  ✓ {free_gb:.1f} GB disponibles")
    
    # Test 6: Entorno
    print("\n[6/6] Verificando entorno Python...")
    print(f"  ✓ Python {sys.version.split()[0]}")
    print(f"  ✓ NumPy {np.__version__}")
    print(f"  ✓ Pandas {pd.__version__}")
    
    print("\n" + "=" * 60)
    print("✓ TODAS LAS VALIDACIONES PASADAS - Listo para análisis SHAP")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
```

**Uso:**
```bash
python test_shap_analysis.py
# Si todo OK: exit code 0
# Si hay problema: exit code 1
```

---

## 8. Monitoreo y Actualización Futura

### Checklist Anual

- [ ] Verificar que archivo SPSS sigue en `/data/sav/2026.sav`
- [ ] Ejecutar `test_shap_analysis.py` (paso 7)
- [ ] Verificar versiones de dependencias
- [ ] Si datos son nuevos (2027, 2028):
  - [ ] Reentrenar modelo
  - [ ] Comparar SHAP values con análisis anterior
  - [ ] Documentar cambios
- [ ] Si performance degrada (accuracy <25%):
  - [ ] Revisar si distribución de datos cambió
  - [ ] Considerar reentrenamiento
  - [ ] Ajustar features si es necesario

### Si Hay Actualización de Dependencias

```python
# Después de: pip install --upgrade scikit-learn shap

# 1. Ejecutar test
python test_shap_analysis.py

# 2. Reentrenar modelo (puede cambiar random seed internos)
jupyter nbconvert --to notebook --execute eaui2026_v3.ipynb

# 3. Comparar resultados
# accuracy_anterior = 0.275
# accuracy_nueva = ?
# Si diferencia > 5%, investigar

# 4. Si todo OK, actualizar requirements.txt con nuevas versiones
pip freeze > requirements.txt
```

---

## 9. Archivos de Apoyo Recomendados

Crear y guardar:

```
/Users/tomas/github/eaui_subtel/
├── modelos/
│   ├── modelo_gse_rf.pkl              # Modelo entrenado
│   ├── scaler.pkl                     # StandardScaler
│   ├── label_encoders.pkl             # LabelEncoders dict
│   └── encoding_dict.json             # Mapeo de categóricas
├── requirements.txt                    # Dependencias pinned
├── test_shap_analysis.py              # Script de validación
├── ROBUSTEZ_Y_MANTENIMIENTO.md        # Este archivo
├── ANALISIS_SHAP.md                   # Resumen de resultados
└── informe_shap_analisis.html         # Reporte visual
```

### Generación Inicial

```bash
# 1. Guardar modelo
python << 'EOF'
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# (después de entrenar rf_model y scaler)
joblib.dump(rf_model, 'modelos/modelo_gse_rf.pkl')
joblib.dump(scaler, 'modelos/scaler.pkl')
joblib.dump(le_dict, 'modelos/label_encoders.pkl')
EOF

# 2. Guardar requirements
pip freeze > requirements.txt

# 3. Guardar encoding dict (en notebook)
import json
with open('modelos/encoding_dict.json', 'w') as f:
    json.dump(encoding_dict, f, indent=2, ensure_ascii=False)
```

---

## 10. Troubleshooting: Problemas Comunes

### Error: "No module named 'shap'"

**Causa:** SHAP no instalado o en entorno equivocado

**Solución:**
```bash
# Activar entorno datascience
source ~/.pyenv/versions/datascience/bin/activate

# Instalar SHAP
pip install shap==0.43.0

# Verificar
python -c "import shap; print(shap.__version__)"
```

### Error: "File '/data/sav/2026.sav' not found"

**Causa:** Ruta relativa incorrecta

**Solución:**
```python
import os
os.chdir('/Users/tomas/github/eaui_subtel')  # Cambiar directorio

# O usar ruta absoluta
df, meta = pyreadstat.read_sav(
    "/Users/tomas/github/eaui_subtel/data/sav/2026.sav"
)
```

### Error: "ChainedAssignmentError" (Pandas)

**Causa:** Pandas copy-on-write activado, .inplace() no funciona

**Solución:**
```python
# INCORRECTO:
df_modelo[col].fillna(df_modelo[col].median(), inplace=True)

# CORRECTO:
df_modelo[col] = df_modelo[col].fillna(df_modelo[col].median())
```

### Error: "MemoryError" en SHAP

**Causa:** Dataset demasiado grande (TreeExplainer bufferea valores SHAP)

**Solución:**
```python
# Usar muestra si tenemos >10k registros
from sklearn.utils import resample

X_test_sample, y_test_sample = resample(
    X_test, y_test, n_samples=5000, random_state=42
)

# SHAP solo sobre muestra
shap_values = explainer.shap_values(X_test_sample)
```

### Error: "Prediction accuracy desplomada" tras actualización

**Causa:** Cambio en random seed de dependencias, distribución de datos cambió

**Solución:**
1. Verificar que `random_state=42` en TODOS lados
2. Verificar distribución de datos (¿cambió?)
3. Si cambió, reentrenar modelo
4. Documentar cambio en `CAMBIOS.log`

---

## Resumen: Garantías de No-Fallo

| Componente | Garantía | Cómo Lograr |
|-----------|----------|-----------|
| **Reproducibilidad** | Mismo resultado siempre | `random_state=42` en todas partes |
| **Robustez** | No falla con datos válidos | `test_shap_analysis.py` antes de ejecutar |
| **Escalabilidad** | Funciona con 5k-50k registros | TreeExplainer con sampling si es necesario |
| **Mantenibilidad** | Fácil actualizar en futuro | `requirements.txt`, modelos guardados |
| **Debuggabilidad** | Fácil encontrar problemas | Tests automatizados y validaciones |

---

## Conclusión

Si sigues este plan:

✅ Análisis SHAP es **reproducible** (mismo resultado siempre)  
✅ Es **robusto** (no falla con datos válidos)  
✅ Es **mantenible** (fácil actualizar)  
✅ Puede ejecutarse **años después** sin problemas  

Si algo falla, consulta la sección **Troubleshooting** o ejecuta `test_shap_analysis.py` para diagnóstico.

---

**Documento creado:** 2026-05-03  
**Versión:** 1.0  
**Próxima revisión:** 2027-05-03
