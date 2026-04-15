# 📊 Encuesta de Acceso y Usos de Internet (SUBTEL) – Chile

Repositorio que consolida datasets y notebooks de análisis de la **Encuesta de Acceso y Usos de Internet**, levantada por la Subsecretaría de Telecomunicaciones de Chile.

---

## 📌 Descripción

La **Encuesta de Acceso y Usos de Internet**, desarrollada por la Subsecretaría de Telecomunicaciones (SUBTEL), es el principal instrumento estadístico a nivel nacional para caracterizar el acceso, uso y condiciones de conectividad digital de la población en Chile. Con un diseño transversal y representatividad nacional y regional, la encuesta recoge información sociodemográfica de las personas, junto con antecedentes sobre acceso a internet, dispositivos utilizados, tipo de conexión y finalidades de uso, constituyéndose en una fuente clave para el seguimiento de la conectividad y la formulación de políticas públicas orientadas a la inclusión digital.

Dado que la encuesta no corresponde a un panel longitudinal, cada levantamiento anual representa una fotografía independiente del estado de la conectividad digital en el país. En este contexto, los datos resultan especialmente adecuados para análisis explicativos orientados a identificar determinantes estructurales del acceso a internet, más que trayectorias individuales en el tiempo. En coherencia con este enfoque, el presente estudio utiliza modelos de aprendizaje supervisado explicables para analizar cómo variables socioeconómicas, educativas, demográficas y territoriales se asocian con la probabilidad de acceso a internet, controlando explícitamente por el uso de proxies tecnológicos y evitando interpretaciones espurias de evolución temporal.

La Encuesta de Acceso y Usos de Internet de la Subsecretaría de Telecomunicaciones (SUBTEL) es un instrumento estadístico de alcance nacional que recoge información sobre el acceso y uso de internet de la población en Chile. La encuesta tiene un diseño transversal y representatividad nacional y regional, e incluye variables sociodemográficas básicas junto con antecedentes sobre conectividad, dispositivos y formas de acceso a internet.

Dado que cada levantamiento anual corresponde a una medición independiente y no a un panel longitudinal, la encuesta permite analizar patrones generales de acceso a internet más que trayectorias individuales en el tiempo. En este contexto, los datos son especialmente adecuados para estudiar la brecha digital desde una perspectiva estructural, lo que justifica el uso de modelos explicativos que analizan la relación entre el acceso a internet y factores socioeconómicos, educativos, demográficos y territoriales.

---

## 🗂️ Contenido del repositorio

Este repositorio contiene:

- 📁 **Datasets originales** de la encuesta (formato a definir: `.sav`, `.csv`, `.dta`, etc.)
- 📓 **Jupyter Notebooks** con:
  - Limpieza y procesamiento de datos
  - Construcción de variables
  - Análisis exploratorio
  - Modelos explicativos de acceso a internet
- 📄 Documentación metodológica

---

## 📅 Encuestas incluidas

Este repositorio contempla **8 levantamientos independientes** de la encuesta:

- 2012  
- 2013  
- 2015  
- 2016  
- 2017  
- 2018  
- 2024  
- 2025  

> ⚠️ Nota: Cada encuesta corresponde a un corte transversal independiente y no a un seguimiento longitudinal de individuos.

---

## 🔬 Variables del estudio y su operacionalización

A continuación se presenta una **tabla formal de variables**, adecuada para una **sección de Datos y Variables** en informe técnico, tesis o artículo académico. Está alineada con el **modelo final explicativo**.

### Variables utilizadas en el análisis del acceso a internet

| Variable                 | Nombre en base de datos | Tipo                  | Operacionalización                                                             | Rol en el modelo            |
| ------------------------ | ----------------------- | --------------------- | ------------------------------------------------------------------------------ | --------------------------- |
| **Acceso a internet**    | `acceso_int`            | Dicotómica            | 1 = Sí tiene acceso a internet; 0 = No tiene acceso                            | Variable dependiente        |
| **Quintil de ingreso**   | `quintil`               | Categórica ordinal    | Q1 (menor ingreso) a Q5 (mayor ingreso)                                        | Determinante socioeconómico |
| **Nivel educacional**    | `niveduc`               | Categórica ordinal    | Desde “sin educación formal” hasta “educación superior universitaria completa” | Determinante estructural    |
| **Edad**                 | `edad`                  | Numérica continua     | Edad en años cumplidos                                                         | Variable demográfica        |
| **Tramo etario**         | `edad_tramo`            | Categórica ordinal    | Agrupación de edad en intervalos etarios (ej. 18–20, 21–25, …, 76+)            | Ciclo de vida               |
| **Zona de residencia**   | `zona`                  | Categórica dicotómica | Urbano / Rural                                                                 | Determinante territorial    |
| **Región de residencia** | `region`                | Categórica nominal    | Región administrativa de residencia                                            | Control territorial         |
| **Sexo**                 | `sexo`                  | Categórica dicotómica | Hombre / Mujer                                                                 | Variable de control         |
| **Año de encuesta**      | `anno`                  | Numérica continua     | Año de aplicación de la encuesta                                               | Variable temporal           |

---

### Variables excluidas del modelo final

| Variable         | Motivo de exclusión                                      |
| ---------------- | -------------------------------------------------------- |
| `tipo_acceso`    | Proxy directo del acceso a internet                      |
| `usa_computador` | Variable tecnológicamente tautológica respecto al acceso |
| `usa_smartphone` | Proxy directo del acceso                                 |

---

### Nota metodológica

El modelo final se construye exclusivamente a partir de variables estructurales y demográficas, excluyendo predictores tecnológicos directos y efectos espurios de calendario, con el fin de maximizar la validez explicativa del análisis de la brecha digital.

---

## ⚙️ Uso del repositorio

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git