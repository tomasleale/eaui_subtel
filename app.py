import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="EAUI 2026 — Dashboard de Conectividad",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.title("📡 EAUI 2026 — Dashboard de Acceso a Internet")
st.markdown("**Encuesta de Acceso y Uso de Internet** — Análisis interactivo de conectividad en Chile")

# ============================================================================
# 1. CARGAR DATOS
# ============================================================================

@st.cache_data
def load_data():
    """Carga datos procesados del CSV"""
    df = pd.read_csv('data/2026_procesado.csv')
    return df

try:
    df = load_data()
    st.sidebar.success(f"✓ Datos cargados: {len(df):,} hogares")
except FileNotFoundError:
    st.error("❌ Error: No se encontró 'data/2026_procesado.csv'")
    st.stop()

# ============================================================================
# 2. SIDEBAR — FILTROS
# ============================================================================

st.sidebar.header("⚙️ Filtros")

# Filtro por región
regiones = ['Todas'] + sorted(df['region'].dropna().unique().tolist())
region_sel = st.sidebar.selectbox("Región", regiones)

# Filtro por zona
zonas = ['Todas'] + sorted(df['zona'].dropna().unique().tolist())
zona_sel = st.sidebar.selectbox("Zona", zonas)

# Filtro por GSE
gse_options = ['Todos'] + sorted(df['gse'].dropna().unique().tolist())
gse_sel = st.sidebar.selectbox("Nivel Socioeconómico (GSE)", gse_options)

# Aplicar filtros
df_filtered = df.copy()
if region_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['region'] == region_sel]
if zona_sel != 'Todas':
    df_filtered = df_filtered[df_filtered['zona'] == zona_sel]
if gse_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['gse'] == gse_sel]

st.sidebar.info(f"📊 Registros mostrados: {len(df_filtered):,} / {len(df):,}")

# ============================================================================
# 3. KPIs — INDICADORES PRINCIPALES
# ============================================================================

st.header("📊 Indicadores Clave (KPIs)")

col1, col2, col3, col4 = st.columns(4)

# KPI 1: % Acceso a Internet
with col1:
    pct_acceso = (df_filtered['acceso_internet_hogar'].eq('Sí').sum() / len(df_filtered) * 100) \
                    if len(df_filtered) > 0 else 0
    st.metric(
        label="Acceso a Internet",
        value=f"{pct_acceso:.1f}%",
        delta="Hogares conectados"
    )

# KPI 2: Smartphones promedio
with col2:
    smartphones_prom = df_filtered['n_smartphones_hogar'].mean()
    st.metric(
        label="Smartphones por Hogar",
        value=f"{smartphones_prom:.1f}",
        delta="Promedio"
    )

# KPI 3: Computadores promedio
with col3:
    computadores_prom = df_filtered['n_computadores_hogar'].mean()
    st.metric(
        label="Computadores por Hogar",
        value=f"{computadores_prom:.1f}",
        delta="Promedio"
    )

# KPI 4: Pago mensual promedio
with col4:
    pago_prom = df_filtered['pago_mensual_internet'].replace(0, np.nan).mean()
    st.metric(
        label="Gasto Mensual Internet",
        value=f"${pago_prom:,.0f}" if pd.notna(pago_prom) else "N/D",
        delta="CLP promedio"
    )

# ============================================================================
# 4. ANÁLISIS DEMOGRÁFICO — BRECHA DIGITAL
# ============================================================================

st.header("👥 Análisis Demográfico — Brecha Digital")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Por Edad", "Por GSE", "Por Zona", "Por Región"]
)

# TAB 1: Acceso por edad
with tab1:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        # Gráfico: Acceso por tramo de edad
        df_edad = df_filtered[df_filtered['tramo_edad'].notna()].copy()
        acceso_edad = df_edad.groupby('tramo_edad')['acceso_internet_hogar'].apply(
            lambda x: (x == 'Sí').sum() / len(x) * 100
        ).sort_values(ascending=False)

        fig = px.bar(
            x=acceso_edad.index,
            y=acceso_edad.values,
            labels={'x': 'Tramo de Edad', 'y': 'Acceso (%)'},
            color=acceso_edad.values,
            color_continuous_scale="Blues"
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("Mayor acceso", f"{acceso_edad.idxmax()}")
        st.metric("Menor acceso", f"{acceso_edad.idxmin()}")
        st.metric("Brecha", f"{acceso_edad.max() - acceso_edad.min():.1f}%")

# TAB 2: Acceso por GSE
with tab2:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        df_gse = df_filtered[df_filtered['gse'].notna()].copy()
        acceso_gse = df_gse.groupby('gse')['acceso_internet_hogar'].apply(
            lambda x: (x == 'Sí').sum() / len(x) * 100
        ).sort_values(ascending=False)

        fig = px.bar(
            x=acceso_gse.index,
            y=acceso_gse.values,
            labels={'x': 'Nivel Socioeconómico', 'y': 'Acceso (%)'},
            color=acceso_gse.values,
            color_continuous_scale="Greens"
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("Mayor acceso", f"{acceso_gse.idxmax()}")
        st.metric("Menor acceso", f"{acceso_gse.idxmin()}")
        st.metric("Brecha", f"{acceso_gse.max() - acceso_gse.min():.1f}%")

# TAB 3: Acceso por zona
with tab3:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        df_zona = df_filtered[df_filtered['zona'].notna()].copy()
        acceso_zona = df_zona.groupby('zona')['acceso_internet_hogar'].apply(
            lambda x: (x == 'Sí').sum() / len(x) * 100
        ).sort_values(ascending=False)

        fig = px.bar(
            x=acceso_zona.index,
            y=acceso_zona.values,
            labels={'x': 'Zona', 'y': 'Acceso (%)'},
            color=acceso_zona.values,
            color_continuous_scale="Oranges"
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("Mayor acceso", f"{acceso_zona.idxmax()}")
        st.metric("Menor acceso", f"{acceso_zona.idxmin()}")
        st.metric("Brecha", f"{acceso_zona.max() - acceso_zona.min():.1f}%")

# TAB 4: Top 10 regiones
with tab4:
    df_reg = df_filtered[df_filtered['region'].notna()].copy()
    acceso_reg = df_reg.groupby('region')['acceso_internet_hogar'].apply(
        lambda x: (x == 'Sí').sum() / len(x) * 100
    ).sort_values(ascending=True).tail(10)

    fig = px.bar(
        y=acceso_reg.index,
        x=acceso_reg.values,
        labels={'x': 'Acceso (%)', 'y': 'Región'},
        color=acceso_reg.values,
        color_continuous_scale="Purples",
        orientation='h'
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 5. DISPOSITIVOS Y TECNOLOGÍAS
# ============================================================================

st.header("💻 Dispositivos y Tecnologías")

col1, col2, col3 = st.columns(3)

# Gráfico 1: Distribución de dispositivos
with col1:
    st.subheader("Equipamiento Promedio")

    dispositivos = {
        'Smartphones': df_filtered['n_smartphones_hogar'].mean(),
        'Computadores': df_filtered['n_computadores_hogar'].mean(),
    }

    fig = px.pie(
        values=list(dispositivos.values()),
        names=list(dispositivos.keys()),
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 2: Tipo de acceso fijo
with col2:
    st.subheader("Tipo de Acceso Fijo")

    df_acceso = df_filtered[df_filtered['tipo_acceso_fijo'].notna()].copy()
    tipo_acceso = df_acceso['tipo_acceso_fijo'].value_counts().head(6)

    fig = px.pie(
        values=tipo_acceso.values,
        names=tipo_acceso.index,
    )
    st.plotly_chart(fig, use_container_width=True)

# Gráfico 3: Velocidad contratada
with col3:
    st.subheader("Velocidad Contratada")

    df_vel = df_filtered[df_filtered['velocidad_contratada'].notna()].copy()
    velocidad = df_vel['velocidad_contratada'].value_counts().head(6)

    fig = px.pie(
        values=velocidad.values,
        names=velocidad.index,
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 6. TABLA DETALLADA
# ============================================================================

st.header("📋 Datos Detallados")

cols_mostrar = [
    'id', 'region', 'zona', 'acceso_internet_hogar',
    'n_smartphones_hogar', 'n_computadores_hogar',
    'gse', 'tramo_edad', 'educ', 'pago_mensual_internet'
]

df_tabla = df_filtered[cols_mostrar].head(100).copy()
df_tabla.columns = [
    'ID', 'Región', 'Zona', 'Acceso Internet',
    'Smartphones', 'Computadores',
    'GSE', 'Edad', 'Educación', 'Pago Mensual'
]

st.dataframe(df_tabla, use_container_width=True, height=400)

# ============================================================================
# 7. PIE DE PÁGINA
# ============================================================================

st.divider()
st.markdown("""
---
**Dashboard EAUI 2026** — Encuesta de Acceso y Uso de Internet
Datos procesados: 5,000 hogares
Última actualización: 2026-05-03

💡 **Cómo publicar este dashboard:**
1. Instala Streamlit: `pip install streamlit`
2. Ejecuta localmente: `streamlit run app.py`
3. Publica en Streamlit Cloud: [streamlit.io/cloud](https://streamlit.io/cloud)
   - Conecta tu repo de GitHub y despliega en 1 clic
""")
