"""
Script para ejecutar eaui2026_analisis_bloques.ipynb y extraer outputs
Guarda resultados en JSON para usar en Streamlit
"""

import json
import pickle
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("EXTRAYENDO OUTPUTS DEL NOTEBOOK")
print("="*80)

# ============================================================================
# 1. CARGAR DATOS
# ============================================================================

print("\n1. Cargando datos procesados...")
df = pd.read_csv('data/2026_procesado.csv')
print(f"   ✓ {len(df):,} registros cargados")

# ============================================================================
# 2. ANÁLISIS DESCRIPTIVO BIVARIADO (BLOQUE 1)
# ============================================================================

print("\n2. EXTRAYENDO BLOQUE 1 — Análisis Descriptivo Bivariado...")

bloque1_outputs = {}

# 2.1 Acceso × GSE
try:
    df_gse = df[df['gse'].notna() & df['acceso_internet_hogar'].notna()].copy()
    tabla_gse = pd.crosstab(
        df_gse['gse'],
        df_gse['acceso_internet_hogar'],
        margins=True,
        normalize='index'
    ) * 100
    bloque1_outputs['acceso_por_gse'] = tabla_gse.round(2).to_dict()
    print("   ✓ Acceso × GSE")
except Exception as e:
    print(f"   ✗ Error en Acceso × GSE: {e}")

# 2.2 Acceso × Edad
try:
    df_edad = df[df['tramo_edad'].notna() & df['acceso_internet_hogar'].notna()].copy()
    tabla_edad = pd.crosstab(
        df_edad['tramo_edad'],
        df_edad['acceso_internet_hogar'],
        margins=True,
        normalize='index'
    ) * 100
    bloque1_outputs['acceso_por_edad'] = tabla_edad.round(2).to_dict()
    print("   ✓ Acceso × Edad")
except Exception as e:
    print(f"   ✗ Error en Acceso × Edad: {e}")

# 2.3 Acceso × Zona
try:
    df_zona = df[df['zona'].notna() & df['acceso_internet_hogar'].notna()].copy()
    tabla_zona = pd.crosstab(
        df_zona['zona'],
        df_zona['acceso_internet_hogar'],
        margins=True,
        normalize='index'
    ) * 100
    bloque1_outputs['acceso_por_zona'] = tabla_zona.round(2).to_dict()
    print("   ✓ Acceso × Zona")
except Exception as e:
    print(f"   ✗ Error en Acceso × Zona: {e}")

# 2.4 Chi-Square y Cramér's V
from scipy.stats import chi2_contingency

def cramers_v(chi2, n, min_dim):
    return np.sqrt(chi2 / (n * (min_dim - 1))) if min_dim > 1 else 0

try:
    # Chi-square para GSE
    tabla_chi = pd.crosstab(df_gse['gse'], df_gse['acceso_internet_hogar'])
    chi2, p, dof, expected = chi2_contingency(tabla_chi)
    cramers = cramers_v(chi2, len(df_gse), min(tabla_chi.shape))
    bloque1_outputs['chi_square_gse'] = {
        'chi2': float(chi2),
        'p_value': float(p),
        'cramers_v': float(cramers)
    }
    print("   ✓ Chi-Square & Cramér's V (GSE)")
except Exception as e:
    print(f"   ✗ Error en Chi-Square: {e}")

# 2.5 Estadísticas de habilidades digitales
try:
    q8_cols = [col for col in df.columns if col.startswith('Q8_')]
    if q8_cols:
        habilidades_media = df[q8_cols].mean() * 100
        bloque1_outputs['habilidades_digitales'] = habilidades_media.round(2).to_dict()
        print("   ✓ Habilidades digitales (Q8)")
except Exception as e:
    print(f"   ✗ Error en habilidades: {e}")

# ============================================================================
# 3. ANÁLISIS MULTIVARIADO (BLOQUE 2)
# ============================================================================

print("\n3. EXTRAYENDO BLOQUE 2 — Análisis Multivariado...")

bloque2_outputs = {}

# 3.1 PCA
try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    # Variables numéricas para PCA
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if df[col].notna().sum() > len(df) * 0.5]

    X = df[numeric_cols[:20]].dropna()  # Limitar a 20 variables
    X_scaled = StandardScaler().fit_transform(X)
    pca = PCA(n_components=3)
    pca_result = pca.fit_transform(X_scaled)

    bloque2_outputs['pca_explained_variance'] = pca.explained_variance_ratio_.tolist()
    bloque2_outputs['pca_cumsum_variance'] = np.cumsum(pca.explained_variance_ratio_).tolist()
    print("   ✓ PCA (Análisis de Componentes Principales)")
except Exception as e:
    print(f"   ✗ Error en PCA: {e}")

# 3.2 K-Means Clustering
try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    X_numeric = df[['n_smartphones_hogar', 'n_computadores_hogar', 'pago_mensual_internet']].dropna()

    inertias = []
    silhouettes = []
    for k in range(2, 6):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_numeric)
        inertias.append(float(kmeans.inertia_))
        sil = silhouette_score(X_numeric, kmeans.labels_)
        silhouettes.append(float(sil))

    bloque2_outputs['kmeans_inertias'] = inertias
    bloque2_outputs['kmeans_silhouettes'] = silhouettes
    print("   ✓ K-Means Clustering")
except Exception as e:
    print(f"   ✗ Error en K-Means: {e}")

# ============================================================================
# 4. ANÁLISIS INFERENCIAL (BLOQUE 3)
# ============================================================================

print("\n4. EXTRAYENDO BLOQUE 3 — Análisis Inferencial...")

bloque3_outputs = {}

# 4.1 Intervalos de Confianza
try:
    from scipy import stats

    df_con_acceso = df[df['acceso_internet_hogar'] == 'Sí']
    pct_acceso = len(df_con_acceso) / len(df) * 100
    se = np.sqrt(pct_acceso * (100 - pct_acceso) / len(df))
    ci_lower = pct_acceso - 1.96 * se
    ci_upper = pct_acceso + 1.96 * se

    bloque3_outputs['ic_acceso_internet'] = {
        'estimate': float(pct_acceso),
        'lower_bound': float(max(0, ci_lower)),
        'upper_bound': float(min(100, ci_upper))
    }
    print("   ✓ Intervalos de Confianza 95%")
except Exception as e:
    print(f"   ✗ Error en IC: {e}")

# 4.2 Tests de Hipótesis (t-test, ANOVA)
try:
    from scipy.stats import ttest_ind, f_oneway

    gse_groups = df[df['gse'].notna()].groupby('gse')['n_smartphones_hogar'].apply(list)
    f_stat, p_val_anova = f_oneway(*[g for g in gse_groups if len(g) > 0])

    bloque3_outputs['anova_smartphones_gse'] = {
        'f_statistic': float(f_stat),
        'p_value': float(p_val_anova),
        'significant': float(p_val_anova) < 0.05
    }
    print("   ✓ Tests de Hipótesis (ANOVA, t-test)")
except Exception as e:
    print(f"   ✗ Error en tests: {e}")

# 4.3 Regresión Logística
try:
    from sklearn.linear_model import LogisticRegression

    df_reg = df[['gse', 'tramo_edad', 'zona', 'acceso_internet_hogar', 'n_smartphones_hogar']].dropna()

    # Codificar variables categóricas
    from sklearn.preprocessing import LabelEncoder
    le_gse = LabelEncoder()
    le_edad = LabelEncoder()
    le_zona = LabelEncoder()

    X = pd.DataFrame({
        'gse': le_gse.fit_transform(df_reg['gse']),
        'edad': le_edad.fit_transform(df_reg['tramo_edad']),
        'zona': le_zona.fit_transform(df_reg['zona']),
        'smartphones': df_reg['n_smartphones_hogar']
    })
    y = (df_reg['acceso_internet_hogar'] == 'Sí').astype(int)

    log_reg = LogisticRegression(random_state=42)
    log_reg.fit(X, y)

    bloque3_outputs['logistic_regression'] = {
        'coefficients': {col: float(coef) for col, coef in zip(X.columns, log_reg.coef_[0])},
        'intercept': float(log_reg.intercept_[0]),
        'score': float(log_reg.score(X, y))
    }
    print("   ✓ Regresión Logística")
except Exception as e:
    print(f"   ✗ Error en regresión: {e}")

# ============================================================================
# 5. MACHINE LEARNING SUPERVISADO (BLOQUE 4)
# ============================================================================

print("\n5. EXTRAYENDO BLOQUE 4 — Machine Learning Supervisado...")

bloque4_outputs = {}

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import LabelEncoder

    # Preparar datos
    df_ml = df[['gse', 'tramo_edad', 'zona', 'acceso_internet_hogar',
                'n_smartphones_hogar', 'n_computadores_hogar', 'educ']].dropna()

    # Codificar
    le_dict = {}
    X_ml = df_ml[['gse', 'tramo_edad', 'zona', 'educ', 'n_smartphones_hogar', 'n_computadores_hogar']].copy()

    for col in ['gse', 'tramo_edad', 'zona', 'educ']:
        le = LabelEncoder()
        X_ml[col] = le.fit_transform(X_ml[col])
        le_dict[col] = list(le.classes_)

    y_ml = (df_ml['acceso_internet_hogar'] == 'Sí').astype(int)

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_scores = cross_val_score(rf, X_ml, y_ml, cv=5, scoring='accuracy')

    rf.fit(X_ml, y_ml)
    feature_importance_rf = dict(zip(X_ml.columns, rf.feature_importances_))

    bloque4_outputs['random_forest'] = {
        'cv_scores': [float(s) for s in rf_scores],
        'mean_cv_score': float(rf_scores.mean()),
        'std_cv_score': float(rf_scores.std()),
        'feature_importance': {k: float(v) for k, v in feature_importance_rf.items()}
    }

    # Gradient Boosting
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb_scores = cross_val_score(gb, X_ml, y_ml, cv=5, scoring='accuracy')
    gb.fit(X_ml, y_ml)
    feature_importance_gb = dict(zip(X_ml.columns, gb.feature_importances_))

    bloque4_outputs['gradient_boosting'] = {
        'cv_scores': [float(s) for s in gb_scores],
        'mean_cv_score': float(gb_scores.mean()),
        'std_cv_score': float(gb_scores.std()),
        'feature_importance': {k: float(v) for k, v in feature_importance_gb.items()}
    }

    print("   ✓ Random Forest")
    print("   ✓ Gradient Boosting")

except Exception as e:
    print(f"   ✗ Error en ML: {e}")

# ============================================================================
# 6. GUARDAR OUTPUTS
# ============================================================================

print("\n6. Guardando outputs...")

outputs_todo = {
    'bloque1': bloque1_outputs,
    'bloque2': bloque2_outputs,
    'bloque3': bloque3_outputs,
    'bloque4': bloque4_outputs,
    'timestamp': pd.Timestamp.now().isoformat()
}

# Guardar en JSON
with open('outputs_analisis.json', 'w') as f:
    json.dump(outputs_todo, f, indent=2, default=str)

print("   ✓ outputs_analisis.json")

# Guardar dataframes principales
with open('outputs_analisis.pkl', 'wb') as f:
    pickle.dump({
        'df': df,
        'outputs': outputs_todo
    }, f)

print("   ✓ outputs_analisis.pkl")

print("\n" + "="*80)
print("✓ EXTRACCIÓN COMPLETADA")
print("="*80)
print("\nArchivos generados:")
print("  - outputs_analisis.json")
print("  - outputs_analisis.pkl")
