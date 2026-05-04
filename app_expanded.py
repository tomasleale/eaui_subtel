import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="EAUI 2026 — Dashboard Completo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 EAUI 2026 — Dashboard Completo de Análisis")
st.markdown("""
**Encuesta de Acceso y Uso de Internet (2026)**
Análisis descriptivo, multivariado, inferencial y machine learning supervisado
""")

# ============================================================================
# CARGAR DATOS Y OUTPUTS
# ============================================================================

@st.cache_data
def load_data():
    """Carga datos procesados"""
    return pd.read_csv('data/2026_procesado.csv')

@st.cache_data
def load_analysis_outputs():
    """Carga outputs de análisis"""
    try:
        with open('outputs_analisis.json', 'r') as f:
            return json.load(f)
    except:
        return None

try:
    df = load_data()
    outputs = load_analysis_outputs()
    st.sidebar.success(f"✓ Datos: {len(df):,} hogares | Análisis: Extraídos")
except Exception as e:
    st.error(f"❌ Error cargando datos: {e}")
    st.stop()

# ============================================================================
# SIDEBAR — NAVEGACIÓN
# ============================================================================

st.sidebar.header("🗂️ Navegación")
bloque_sel = st.sidebar.radio(
    "Selecciona bloque de análisis:",
    ["Inicio", "BLOQUE 1: Bivariado", "BLOQUE 2: Multivariado",
     "BLOQUE 3: Inferencial", "BLOQUE 4: Machine Learning"]
)

# ============================================================================
# PÁGINA DE INICIO
# ============================================================================

if bloque_sel == "Inicio":
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pct_acceso = (df['acceso_internet_hogar'].eq('Sí').sum() / len(df) * 100)
        st.metric("Acceso a Internet", f"{pct_acceso:.1f}%", "Hogares conectados")

    with col2:
        smartphones_prom = df['n_smartphones_hogar'].mean()
        st.metric("Smartphones/Hogar", f"{smartphones_prom:.1f}", "Promedio")

    with col3:
        computadores_prom = df['n_computadores_hogar'].mean()
        st.metric("Computadores/Hogar", f"{computadores_prom:.1f}", "Promedio")

    with col4:
        pago_prom = df['pago_mensual_internet'].replace(0, np.nan).mean()
        st.metric("Gasto Internet", f"${pago_prom:,.0f}", "CLP mensual")

    st.divider()

    st.markdown("### 📌 Estructura del Dashboard")
    st.markdown("""
    Este dashboard presenta los resultados de 4 bloques de análisis:

    - **BLOQUE 1: Análisis Descriptivo Bivariado**
      Cruces de tablas, chi-square, Cramér's V, habilidades digitales

    - **BLOQUE 2: Análisis Multivariado**
      PCA, Análisis de Correspondencia, K-Means Clustering

    - **BLOQUE 3: Análisis Inferencial**
      Intervalos de confianza, tests de hipótesis, regresiones logística y ordinal

    - **BLOQUE 4: Machine Learning Supervisado**
      Random Forest, Gradient Boosting, Feature Importance, cross-validation

    Selecciona un bloque en el menú lateral para ver los resultados.
    """)

# ============================================================================
# BLOQUE 1: ANÁLISIS DESCRIPTIVO BIVARIADO
# ============================================================================

elif bloque_sel == "BLOQUE 1: Bivariado":
    st.markdown("### 📊 BLOQUE 1 — Análisis Descriptivo Bivariado")

    if outputs and 'bloque1' in outputs:
        bloque1 = outputs['bloque1']

        # TAB 1: Acceso × GSE
        tab1, tab2, tab3, tab4 = st.tabs(["Acceso × GSE", "Acceso × Edad", "Acceso × Zona", "Habilidades Digitales"])

        with tab1:
            if 'acceso_por_gse' in bloque1:
                st.subheader("Acceso a Internet por Nivel Socioeconómico (GSE)")

                # Tabla
                tabla_gse = pd.DataFrame(bloque1['acceso_por_gse']).T
                st.dataframe(tabla_gse, use_container_width=True)

                # Gráfico
                if 'Sí' in tabla_gse.columns:
                    fig = px.bar(
                        x=tabla_gse.index,
                        y=tabla_gse['Sí'],
                        labels={'x': 'GSE', 'y': 'Acceso (%)'},
                        color=tabla_gse['Sí'],
                        color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Chi-square
            if 'chi_square_gse' in bloque1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Chi-Square", f"{bloque1['chi_square_gse']['chi2']:.2f}")
                with col2:
                    st.metric("p-value", f"{bloque1['chi_square_gse']['p_value']:.4f}")
                with col3:
                    st.metric("Cramér's V", f"{bloque1['chi_square_gse']['cramers_v']:.3f}")

                if bloque1['chi_square_gse']['p_value'] < 0.05:
                    st.success("✓ Asociación significativa (p < 0.05)")
                else:
                    st.warning("✗ Asociación no significativa (p ≥ 0.05)")

        with tab2:
            if 'acceso_por_edad' in bloque1:
                st.subheader("Acceso a Internet por Tramo de Edad")

                tabla_edad = pd.DataFrame(bloque1['acceso_por_edad']).T
                st.dataframe(tabla_edad, use_container_width=True)

                if 'Sí' in tabla_edad.columns:
                    fig = px.bar(
                        x=tabla_edad.index,
                        y=tabla_edad['Sí'],
                        labels={'x': 'Edad', 'y': 'Acceso (%)'},
                        color=tabla_edad['Sí'],
                        color_continuous_scale="Greens"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with tab3:
            if 'acceso_por_zona' in bloque1:
                st.subheader("Acceso a Internet por Zona")

                tabla_zona = pd.DataFrame(bloque1['acceso_por_zona']).T
                st.dataframe(tabla_zona, use_container_width=True)

                if 'Sí' in tabla_zona.columns:
                    fig = px.pie(
                        values=tabla_zona['Sí'],
                        names=tabla_zona.index,
                        title="Distribución de Acceso por Zona"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with tab4:
            if 'habilidades_digitales' in bloque1:
                st.subheader("Habilidades Digitales (Q8)")

                habilidades = pd.Series(bloque1['habilidades_digitales']).sort_values(ascending=False)

                fig = px.bar(
                    x=habilidades.values,
                    y=habilidades.index,
                    labels={'x': 'Prevalencia (%)', 'y': 'Habilidad'},
                    color=habilidades.values,
                    color_continuous_scale="Oranges",
                    orientation='h'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Datos de Bloque 1 no disponibles")

# ============================================================================
# BLOQUE 2: ANÁLISIS MULTIVARIADO
# ============================================================================

elif bloque_sel == "BLOQUE 2: Multivariado":
    st.markdown("### 📈 BLOQUE 2 — Análisis Multivariado")

    if outputs and 'bloque2' in outputs:
        bloque2 = outputs['bloque2']

        tab1, tab2 = st.tabs(["PCA", "K-Means Clustering"])

        with tab1:
            if 'pca_explained_variance' in bloque2:
                st.subheader("PCA — Análisis de Componentes Principales")

                var_explicada = bloque2['pca_explained_variance']
                cumsum_var = bloque2['pca_cumsum_variance']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("PC1 Varianza", f"{var_explicada[0]*100:.1f}%")
                with col2:
                    st.metric("PC2 Varianza", f"{var_explicada[1]*100:.1f}%")
                with col3:
                    st.metric("Varianza Acumulada", f"{cumsum_var[2]*100:.1f}%")

                # Gráfico de varianza acumulada
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=cumsum_var,
                    mode='lines+markers',
                    name='Varianza Acumulada',
                    line=dict(color='blue', width=2)
                ))
                fig.update_layout(
                    title="Varianza Explicada Acumulada",
                    xaxis_title="Componente Principal",
                    yaxis_title="Varianza Acumulada",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            if 'kmeans_inertias' in bloque2:
                st.subheader("K-Means Clustering")

                inertias = bloque2['kmeans_inertias']
                silhouettes = bloque2['kmeans_silhouettes']

                col1, col2 = st.columns(2)

                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=inertias,
                        x=list(range(2, 6)),
                        mode='lines+markers',
                        name='Inercia',
                        line=dict(color='red', width=2)
                    ))
                    fig.update_layout(
                        title="Inercia vs Número de Clusters",
                        xaxis_title="k",
                        yaxis_title="Inercia",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        y=silhouettes,
                        x=list(range(2, 6)),
                        mode='lines+markers',
                        name='Silhouette',
                        line=dict(color='green', width=2)
                    ))
                    fig.update_layout(
                        title="Silhouette Score vs Número de Clusters",
                        xaxis_title="k",
                        yaxis_title="Silhouette Score",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Datos de Bloque 2 no disponibles")

# ============================================================================
# BLOQUE 3: ANÁLISIS INFERENCIAL
# ============================================================================

elif bloque_sel == "BLOQUE 3: Inferencial":
    st.markdown("### 🔬 BLOQUE 3 — Análisis Inferencial")

    if outputs and 'bloque3' in outputs:
        bloque3 = outputs['bloque3']

        tab1, tab2, tab3 = st.tabs(["IC 95%", "Tests de Hipótesis", "Regresión Logística"])

        with tab1:
            if 'ic_acceso_internet' in bloque3:
                st.subheader("Intervalos de Confianza 95% — Acceso a Internet")

                ic = bloque3['ic_acceso_internet']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Estimador", f"{ic['estimate']:.2f}%")
                with col2:
                    st.metric("Límite Inferior", f"{ic['lower_bound']:.2f}%")
                with col3:
                    st.metric("Límite Superior", f"{ic['upper_bound']:.2f}%")

                # Visualización
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[ic['lower_bound'], ic['estimate'], ic['upper_bound']],
                    y=['IC 95%', 'Estimador', 'IC 95%'],
                    mode='markers+lines',
                    marker=dict(size=15, color=['gray', 'blue', 'gray']),
                    line=dict(color='blue', width=2)
                ))
                fig.update_layout(
                    title="Intervalo de Confianza 95%",
                    xaxis_title="Porcentaje (%)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            if 'anova_smartphones_gse' in bloque3:
                st.subheader("ANOVA — Smartphones × GSE")

                anova = bloque3['anova_smartphones_gse']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("F-Statistic", f"{anova['f_statistic']:.3f}")
                with col2:
                    st.metric("p-value", f"{anova['p_value']:.4f}")
                with col3:
                    if anova['significant']:
                        st.metric("Significancia", "✓ p < 0.05", delta="Significativo")
                    else:
                        st.metric("Significancia", "✗ p ≥ 0.05", delta="No significativo")

        with tab3:
            if 'logistic_regression' in bloque3:
                st.subheader("Regresión Logística — Acceso a Internet")

                reg = bloque3['logistic_regression']

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Accuracy", f"{reg['score']:.3f}")

                with col2:
                    st.metric("Intercept", f"{reg['intercept']:.4f}")

                st.subheader("Coeficientes")
                coef_df = pd.DataFrame(
                    list(reg['coefficients'].items()),
                    columns=['Variable', 'Coeficiente']
                ).sort_values('Coeficiente', ascending=False)

                fig = px.bar(
                    coef_df,
                    x='Coeficiente',
                    y='Variable',
                    color='Coeficiente',
                    color_continuous_scale="RdBu",
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Datos de Bloque 3 no disponibles")

# ============================================================================
# BLOQUE 4: MACHINE LEARNING
# ============================================================================

elif bloque_sel == "BLOQUE 4: Machine Learning":
    st.markdown("### 🤖 BLOQUE 4 — Machine Learning Supervisado")

    if outputs and 'bloque4' in outputs:
        bloque4 = outputs['bloque4']

        tab1, tab2 = st.tabs(["Random Forest", "Gradient Boosting"])

        with tab1:
            if 'random_forest' in bloque4:
                st.subheader("Random Forest — Acceso a Internet")

                rf = bloque4['random_forest']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mean CV Score", f"{rf['mean_cv_score']:.3f}")
                with col2:
                    st.metric("Std CV Score", f"{rf['std_cv_score']:.3f}")
                with col3:
                    st.metric("Cross-Validation", f"5-Fold")

                st.subheader("Feature Importance")
                fi_df = pd.DataFrame(
                    list(rf['feature_importance'].items()),
                    columns=['Feature', 'Importance']
                ).sort_values('Importance', ascending=False)

                fig = px.bar(
                    fi_df,
                    x='Importance',
                    y='Feature',
                    color='Importance',
                    color_continuous_scale="Viridis",
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            if 'gradient_boosting' in bloque4:
                st.subheader("Gradient Boosting — Acceso a Internet")

                gb = bloque4['gradient_boosting']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Mean CV Score", f"{gb['mean_cv_score']:.3f}")
                with col2:
                    st.metric("Std CV Score", f"{gb['std_cv_score']:.3f}")
                with col3:
                    st.metric("Cross-Validation", f"5-Fold")

                st.subheader("Feature Importance")
                fi_df = pd.DataFrame(
                    list(gb['feature_importance'].items()),
                    columns=['Feature', 'Importance']
                ).sort_values('Importance', ascending=False)

                fig = px.bar(
                    fi_df,
                    x='Importance',
                    y='Feature',
                    color='Importance',
                    color_continuous_scale="Plasma",
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Datos de Bloque 4 no disponibles")

# ============================================================================
# PIE DE PÁGINA
# ============================================================================

st.divider()
st.markdown("""
---
**EAUI 2026 — Dashboard Completo de Análisis**
Encuesta de Acceso y Uso de Internet | Datos procesados: 5,000 hogares
""")
