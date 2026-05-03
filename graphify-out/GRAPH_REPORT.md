# Graph Report - .  (2026-05-03)

## Corpus Check
- Corpus is ~12,325 words - fits in a single context window. You may not need a graph.

## Summary
- 27 nodes · 34 edges · 6 communities detected
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.83)
- Token cost: 82,355 input · 18,892 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Data & Skills Architecture|Data & Skills Architecture]]
- [[_COMMUNITY_Classification Model (Improved)|Classification Model (Improved)]]
- [[_COMMUNITY_Policy Implications & Findings|Policy Implications & Findings]]
- [[_COMMUNITY_SHAP & Explainability|SHAP & Explainability]]
- [[_COMMUNITY_Documentation Pipeline|Documentation Pipeline]]
- [[_COMMUNITY_Graph Infrastructure|Graph Infrastructure]]

## God Nodes (most connected - your core abstractions)
1. `Feature Engineering: 4 Variables de Comportamiento` - 5 edges
2. `Behavior > Demographics (Key Finding)` - 5 edges
3. `SHAP Analysis: Explicabilidad del Modelo` - 4 edges
4. `Modelo de Clasificación Mejorado` - 4 edges
5. `EAUI Subtel Data Graph & Resilience Analysis` - 4 edges
6. `n_actividades_online (Feature)` - 4 edges
7. `Análisis Completo EAUI 2026` - 3 edges
8. `Gradient Boosting Classifier` - 3 edges
9. `GSE Derivation (Matriz 2x6)` - 3 edges
10. `nivel_habilidades (Target Variable)` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Resilience: Youth Overcomes Barriers` --semantically_similar_to--> `Behavior > Demographics (Key Finding)`  [INFERRED] [semantically similar]
  GRAPH_INSIGHTS.md → SUMMARY.md
- `GSE Derivation (Matriz 2x6)` --conceptually_related_to--> `Multicolinearity: GSE mediada por actividades`  [INFERRED]
  GRAPH_INSIGHTS.md → SHAP_ANALYSIS.md
- `Access is NOT the Bottleneck (Policy Insight)` --conceptually_related_to--> `Behavior > Demographics (Key Finding)`  [INFERRED]
  SHAP_ANALYSIS.md → SUMMARY.md
- `SHAP Analysis: Explicabilidad del Modelo` --references--> `Gradient Boosting Classifier`  [EXTRACTED]
  SHAP_ANALYSIS.md → CLASSIFICATION_MODEL_IMPROVED.md
- `EAUI 2026: Análisis Completo - README` --references--> `Modelo de Clasificación Mejorado`  [EXTRACTED]
  README_ANALYSIS.md → CLASSIFICATION_MODEL_IMPROVED.md

## Hyperedges (group relationships)
- **Feature Engineering & Classification Pipeline** — feature_engineering, n_actividades_online, frecuencia_internet_feature, gradient_boosting_model, behavior_dominates_demographics [EXTRACTED 0.95]
- **Data Processing & Skills Classification** — eaui2026_v3_ipynb, gse_derivation, data_pipeline, nivel_habilidades, skill_classification_hierarchy [EXTRACTED 0.95]
- **Policy Implications of Feature Importance** — behavior_dominates_demographics, access_not_bottleneck, resilience_finding, permutation_importance [INFERRED 0.85]

## Communities

### Community 0 - "Data & Skills Architecture"
Cohesion: 0.25
Nodes (8): Clase Básico: Persistent Classification Problem, EAUI Subtel Data Graph & Resilience Analysis, GSE Derivation (Matriz 2x6), Income Stratification (3 Groups), nivel_habilidades (Target Variable), Q8_1:Q8_19 (Skills Survey Items), Skill Classification: Hierarchical Levels, Urban-Rural Digital Gap

### Community 1 - "Classification Model (Improved)"
Cohesion: 0.47
Nodes (6): Modelo de Clasificación Mejorado, Feature Engineering: 4 Variables de Comportamiento, frecuencia_internet_num (Feature), Gradient Boosting Classifier, n_actividades_online (Feature), Q21_1:Q21_44 (Online Activities)

### Community 2 - "Policy Implications & Findings"
Cohesion: 0.5
Nodes (5): Access is NOT the Bottleneck (Policy Insight), Análisis Completo EAUI 2026, Behavior > Demographics (Key Finding), Resilience: Youth Overcomes Barriers, EAUI 2026: Resumen Ejecutivo

### Community 3 - "SHAP & Explainability"
Cohesion: 1.0
Nodes (3): Multicolinearity: GSE mediada por actividades, Permutation Importance (Método), SHAP Analysis: Explicabilidad del Modelo

### Community 4 - "Documentation Pipeline"
Cohesion: 1.0
Nodes (2): Data Processing Pipeline, EAUI 2026: Análisis Completo - README

### Community 5 - "Graph Infrastructure"
Cohesion: 1.0
Nodes (1): Graphify Knowledge Graph Report

## Knowledge Gaps
- **6 isolated node(s):** `Graphify Knowledge Graph Report`, `Income Stratification (3 Groups)`, `Q8_1:Q8_19 (Skills Survey Items)`, `Q21_1:Q21_44 (Online Activities)`, `frecuencia_internet_num (Feature)` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Documentation Pipeline`** (2 nodes): `Data Processing Pipeline`, `EAUI 2026: Análisis Completo - README`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Graph Infrastructure`** (1 nodes): `Graphify Knowledge Graph Report`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EAUI Subtel Data Graph & Resilience Analysis` connect `Data & Skills Architecture` to `Policy Implications & Findings`?**
  _High betweenness centrality (0.267) - this node is a cross-community bridge._
- **Why does `Behavior > Demographics (Key Finding)` connect `Policy Implications & Findings` to `Classification Model (Improved)`?**
  _High betweenness centrality (0.240) - this node is a cross-community bridge._
- **Why does `Resilience: Youth Overcomes Barriers` connect `Policy Implications & Findings` to `Data & Skills Architecture`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Behavior > Demographics (Key Finding)` (e.g. with `Resilience: Youth Overcomes Barriers` and `Access is NOT the Bottleneck (Policy Insight)`) actually correct?**
  _`Behavior > Demographics (Key Finding)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Graphify Knowledge Graph Report`, `Income Stratification (3 Groups)`, `Q8_1:Q8_19 (Skills Survey Items)` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._