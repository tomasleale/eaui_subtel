# Plan de análisis univariado — EAUI 2026

**Base:** `data/sav/2026.sav` — 5.000 casos, 587 variables
**Libro de códigos:** `docs/diccionario/libro_codigos_EAUI2026.xlsx`
**Antecede a:** `PLAN_ANALISIS_EAUI2026.md` (bivariado, multivariado, inferencial, ML)

Este plan ordena la primera capa descriptiva: una pasada exhaustiva variable por variable, separando lo que merece análisis ponderado del ruido (variables constantes, abiertas sin codificar, NET redundantes). El objetivo no es producir todas las tablas, sino dejar listo el insumo de diagnóstico para decidir qué variables entran al bloque bivariado y cuáles se recodifican o descartan.

---

## 0. Preparación previa

**Validación de ponderadores.** El libro de códigos lista 4 ponderadores. Conviene confirmar cuál corresponde a hogar (`fe_hogar`) y cuál a individuo (`fe_personas`), y verificar que la suma ponderada se aproxima al marco poblacional 2026 (Censo proyectado, INE).

**Bases efectivas.** Muchas variables tienen `null_count` alto por skip patterns (ej. `P5_1` con n=3.297 sobre 5.000). Para cada variable hay que reportar su base efectiva, no la base total.

**Códigos especiales.** Identificar y mapear NS/NR (típicamente 88, 98, 99) antes de calcular distribuciones. La función `dstats()` debe recibir las variables ya con NaN donde corresponda.

**Inventario inicial.** Cruzar diccionario × tipo × módulo (ya está en la hoja "Variables por tipo" del libro de códigos). Marcar:

- Variables constantes (`valores_unicos = 1`) → descartar.
- Variables casi-constantes (>95% en una categoría) → revisar utilidad.
- Variables NET (334) que duplican información de los ítems individuales → decidir si reportar el agregado o los componentes.

---

## 1. Estrategia por tipo de variable

La distribución de tipos en el libro de códigos sugiere agrupar el análisis en seis flujos paralelos.

### Categóricas nominales (137)

`dstats()` en modo **frecuencia** ponderado. Reportar n, n ponderado, % con 2 decimales, ordenado por `ORDEN_CATEGORIAS` cuando aplique o por frecuencia descendente en caso contrario. Para variables con más de 10 categorías, mostrar top 10 + "Otras" agrupado.

Variables prioritarias del módulo A: `educ_jh`, `ocupacion_jh`, `parentesco_jh`. Del módulo P: tipo de conexión, proveedor, motivos de no acceso. Del módulo Q: las 112 nominales requieren un loop con salida estandarizada.

### Likert ordinal (1)

Frecuencia con orden categórico fijo. Reportar mediana, moda, % en extremos (top-2 y bottom-2 box). Mantener orden en visualizaciones.

### Dicotómicas de respuesta múltiple (88)

Tratar por **bloque temático**, no variable por variable. Ejemplo: `P3_1` a `P3_8` forman un set de menciones; conviene una tabla única con todas las menciones del bloque, su % de "Sí" sobre la base efectiva común, y nota de que la suma supera 100%.

Esto reduce 88 tablas individuales a aproximadamente 12-15 tablas de bloque.

### Agregados NET (334)

Las variables NET son el agregado de respuestas abiertas codificadas. Tratarlas como menciones agrupadas: % por NET sobre base efectiva, una tabla por bloque temático. Antes de generar todas las tablas, decidir con qué granularidad se trabajará downstream — si solo se usarán los NET, los ítems individuales pueden quedar fuera del entregable univariado.

### Conteos enteros (3)

`n_smartphones_hogar`, `n_computadores_hogar`, `parentesco_jh`. Estadísticos: media ponderada, mediana, p25/p50/p75/p90, máximo. Distribución de frecuencia agrupada (0, 1, 2, 3, 4+).

### Montos en pesos (7)

Para variables monetarias la media simple es engañosa por outliers. Reportar mediana, p25/p50/p75/p90, media ponderada con IC 95%. Identificar techo de respuesta (valores tope) y revisar si hay un código de "no aplica" embebido como número.

### Texto abierto (9)

Conteo de respuestas no vacías, longitud promedio, top 20 menciones literales. Si la encuesta no las codifica posteriormente, dejarlas como insumo cualitativo y no incluir en el entregable cuantitativo principal.

### Geográficas y de control (5)

`region`, `zona`, `comuna`: frecuencias ponderadas. Comparar distribución por región contra Censo 2024 proyectado. Para comuna, top 20 + agrupación "Resto" por región. `fecha_fin`: rango y distribución semanal del trabajo de campo.

---

## 2. Estructura de salida estandarizada

Una **tabla maestra univariada** por módulo, formato Excel sin formato, con columnas:

```
variable | etiqueta | modulo | tipo | nivel | base_efectiva | n_pond |
estadistico | valor | ns_nr_pct | observacion
```

El campo `estadistico` toma valores como `%`, `media`, `mediana`, `p75`, etc. Esto permite apilar todas las variables en un solo dataframe largo y filtrarlo después.

Cuatro hojas Excel resultantes:

- `univariado_modulo_A.xlsx` (33 vars)
- `univariado_modulo_P.xlsx` (142 vars, separar conteos/montos/categóricas/NET)
- `univariado_modulo_Q.xlsx` (405 vars, dividir en 2-3 archivos por peso)
- `univariado_control.xlsx` (5 vars)

Decimales: 2 en porcentajes. Separador de miles: coma. Sin formato condicional, colores ni bordes — pegado directo a Word.

---

## 3. Diagnóstico final

Producto separado: `docs/diagnostico_univariado.md` (1-2 páginas) con tres secciones cortas.

**Variables a descartar.** Constantes, casi-constantes >95%, y aquellas con NS/NR > 50%.

**Variables a recodificar antes del bivariado.** Nominales con cardinalidad alta que requieren agrupación, dicotomizaciones útiles (ej. `tiene_internet` desde `acceso_internet_hogar`), tramos de edad, GSE derivado vía AIM-ESOMAR.

**Variables filtro y bases condicionales.** Mapa de los principales skip patterns: qué variable filtra a qué bloque, con la base efectiva de cada filtro. Esto es crítico para evitar errores en bivariado.

---

## 4. Productos esperados

- `notebooks/archivos/eaui2026_univariado.ipynb` — loop por tipo usando `dstats()`, `fordf()`, `mostrar_tabla()`.
- `analysis/univariado/*.xlsx` — tablas maestras por módulo.
- `docs/diagnostico_univariado.md` — observaciones que alimentan el bloque bivariado.
- Gráficos seaborn/matplotlib por demanda (no por defecto, para no inflar el entregable).

---

## 5. Estimación de esfuerzo

| Fase | Horas |
|---|---|
| Validación ponderadores + códigos NS/NR | 1-2 |
| Función dispatcher por tipo de variable | 2-3 |
| Loop de ejecución y exportación | 1 |
| Curaduría tablas + diagnóstico | 3-4 |
| **Total** | **~1 día** |

---

## 6. Decisiones a confirmar antes de empezar

1. ¿Reportar agregados NET o componentes individuales? (recomendación: NET como default, componentes a demanda).
2. ¿Cardinalidad máxima para mostrar todas las categorías nominales? (sugerencia: 10).
3. ¿Incluir IC 95% en todos los porcentajes ponderados o solo en montos/conteos? (sugerencia: solo en montos/conteos para mantener tablas livianas).
4. ¿Las variables Q (individuo) usan `fe_personas` o `fe_hogar` cuando preguntan sobre el hogar? (revisar con manual de la encuesta).
