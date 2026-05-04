# 📊 Dashboard EAUI 2026 — Versión Expandida

Dashboard Streamlit que presenta todos los análisis del notebook `eaui2026_analisis_bloques.ipynb`:

- **BLOQUE 1:** Análisis Descriptivo Bivariado
- **BLOQUE 2:** Análisis Multivariado (PCA, K-Means)
- **BLOQUE 3:** Análisis Inferencial (IC, Tests, Regresión)
- **BLOQUE 4:** Machine Learning Supervisado (Random Forest, Gradient Boosting)

---

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

Asegúrate de que tu `requirements.txt` incluya:
```
streamlit>=1.36.0
pandas>=2.2.0
plotly>=5.20.0
numpy>=1.26.0
scikit-learn>=1.3.0
scipy>=1.11.0
```

### 2. Extraer outputs del notebook
```bash
python extract_notebook_outputs.py
```

Este script:
- ✓ Lee `data/2026_procesado.csv`
- ✓ Realiza análisis descriptivo, multivariado, inferencial y ML
- ✓ Guarda resultados en `outputs_analisis.json` y `outputs_analisis.pkl`

### 3. Ejecutar el dashboard
```bash
streamlit run app_expanded.py
```

Se abrirá en `http://localhost:8501`

---

## 📁 Archivos

| Archivo | Descripción |
|---------|------------|
| `app.py` | Dashboard básico (KPIs, filtros, datos) |
| `app_expanded.py` | **Dashboard completo con 4 bloques de análisis** ⭐ |
| `extract_notebook_outputs.py` | Script para extraer outputs del notebook |
| `requirements.txt` | Dependencias Python |
| `outputs_analisis.json` | Resultados de análisis (JSON) |
| `outputs_analisis.pkl` | Resultados de análisis (pickle) |
| `data/2026_procesado.csv` | Dataset procesado (5,000 registros) |

---

## 📊 Contenido del Dashboard

### BLOQUE 1: Análisis Descriptivo Bivariado
- Tablas de contingencia (Acceso × GSE, Edad, Zona)
- Chi-square y Cramér's V
- Habilidades digitales (Q8)

### BLOQUE 2: Análisis Multivariado
- PCA: Varianza explicada, componentes principales
- K-Means: Inercia, Silhouette score (k=2 a 5)

### BLOQUE 3: Análisis Inferencial
- Intervalos de Confianza 95% para % acceso
- ANOVA: Smartphones × GSE
- Regresión Logística: Coeficientes y accuracy

### BLOQUE 4: Machine Learning
- Random Forest: CV scores, feature importance
- Gradient Boosting: CV scores, feature importance

---

## 🔧 Personalización

### Cambiar datos
Si usas un CSV diferente, modifica la ruta en `extract_notebook_outputs.py`:
```python
df = pd.read_csv('ruta/a/tu/archivo.csv')
```

### Agregar más análisis
Edita `extract_notebook_outputs.py` para incluir análisis adicionales y guarda en `outputs_analisis.json`

### Cambiar tema del dashboard
Modifica la sección `st.markdown` en `app_expanded.py` para personalizar colores y estilos.

---

## 📤 Publicar en Streamlit Cloud

1. Sube tu código a GitHub (incluyendo `outputs_analisis.json`)
2. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
3. Conecta tu repo y selecciona:
   - **Repository:** tu-usuario/eaui_subtel
   - **Branch:** main
   - **Main file:** `app_expanded.py`
4. Click en "Deploy"

---

## ⚠️ Notas Importantes

- El archivo `outputs_analisis.json` debe estar en el repositorio para que el dashboard funcione
- Si modificas el notebook, re-ejecuta `extract_notebook_outputs.py` para actualizar los análisis
- El dashboard carga datos cacheados por Streamlit (muy rápido después de la primera carga)
- Algunos análisis de ML pueden requerir más tiempo en la primera ejecución

---

## 🆘 Solución de Problemas

**Error: "outputs_analisis.json no encontrado"**
```bash
python extract_notebook_outputs.py
```

**Error: "ModuleNotFoundError: No module named 'sklearn'"**
```bash
pip install scikit-learn --break-system-packages
```

**Streamlit es lento**
- Asegúrate de que `@st.cache_data` está en las funciones de carga
- Ejecuta el script de extracción una sola vez antes de usar

---

## 📧 Contacto

Para preguntas o sugerencias sobre el dashboard, contacta al equipo de análisis.
