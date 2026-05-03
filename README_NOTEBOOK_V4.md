# eaui2026_v4.ipynb - Análisis SHAP Completo

## ✅ Estado: Notebook LISTO PARA EJECUTAR

### Contenido (14 celdas):

1. **Carga de Librerías** - Importar dependencias
2. **Carga de Datos** - SPSS 2026 (5,000 registros)
3. **Procesamiento GSE** - Cálculo de Grupo Socioeconómico
4. **Ingeniería de Features** - Creación de variables derivadas
5. **Preparación del Modelo** - Limpieza, codificación, normalización
6. **Entrenamiento** - Random Forest (100 árboles, max_depth=15)
7. **Feature Importance** - Análisis tradicional + visualizaciones
8. **SHAP Analysis** - Cálculo de valores SHAP
9. **Comparación** - SHAP vs Feature Importance (gráficos lado a lado)
10. **Resumen Final** - Reporte completo de resultados

### Cómo Ejecutar:

**Opción 1: Jupyter Notebook Interactivo**
```bash
cd /Users/tomas/github/eaui_subtel
jupyter notebook eaui2026_v4.ipynb
```

**Opción 2: Ejecutar todas las celdas**
```bash
~/.pyenv/versions/datascience/bin/python -m jupyter nbconvert \
  --to notebook --execute eaui2026_v4.ipynb \
  --output eaui2026_v4_ejecutado.ipynb
```

### Outputs Esperados:

✓ **Gráficos**
- Matriz de Confusión
- Top 10 Features (Feature Importance)
- Top 10 Features (SHAP)
- Comparación SHAP vs Feature Importance

✓ **Archivo CSV**
- `shap_ranking.csv` - Ranking de features por importancia SHAP

✓ **Consola**
- Accuracy del modelo
- Reporte de clasificación
- Top 5 features SHAP
- Resumen final

### Features Utilizados (9 total):

**Numéricos (6):**
- edad
- n_dispositivos (derivado)
- n_actividades (derivado)
- intensidad (derivado)
- pago_internet
- pago_movil

**Categóricos (3):**
- sexo (Hombre/Mujer)
- zona (Urbana/Rural)
- uso_smartphone (Sí/No)

### Documentación Complementaria:

- **ANALISIS_SHAP.md** - Interpretación detallada de resultados
- **informe_shap_analisis.html** - Reporte visual en HTML
- **ROBUSTEZ_Y_MANTENIMIENTO.md** - Garantías de reproducibilidad

### Dependencias:

```
pyreadstat>=1.2.0
pandas>=2.0.0
numpy>=1.23.0
scikit-learn>=1.3.0
shap>=0.43.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

Todas están instaladas en el entorno `datascience`.

### Notas:

- Random State = 42 (reproducible)
- Train/Test Split = 80/20
- Normalización: StandardScaler
- Class Weight: balanced (para desbalance de clases)
- Timeout recomendado: 5 minutos

