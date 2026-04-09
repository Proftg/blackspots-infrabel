# 🗺️ Blackspots Infrabel — Cartographie & Machine Learning

Analyse de **22+ millions d'enregistrements** Open Data Infrabel pour identifier, classifier et **prédire** les gares problématiques du réseau ferroviaire belge.

## 🎯 Objectifs

- **Cartographier** les points noirs géographiques du réseau (HeatMap Folium)
- **Détecter** les anomalies statistiques par gare (Isolation Forest)
- **Prédire** les gares à risque avant dégradation des KPIs (XGBoost)
- **Analyser** les tendances temporelles et la saisonnalité (STL Decomposition)

## 📊 Résultats

- **14 mois** de données analysées (jan 2025 → fév 2026)
- **19,7M+** d'enregistrements traités
- **660 gares** uniques · **172 lignes** ferroviaires
- **Carte interactive** des points noirs avec HeatMap pondérée
- **4 modèles ML** : DBSCAN · Isolation Forest · STL · XGBoost

## 🤖 Extension Machine Learning (`blackspots_ml.ipynb`)

### DBSCAN — Clustering Géographique
Identification des zones géographiques concentrant les retards par regroupement spatial des gares. Distance haversine, eps = 15 km.

### Isolation Forest — Détection d'Anomalies
Détection des gares au comportement statistiquement atypique (~10% du réseau). Identifie les situations anormales indépendamment des seuils arbitraires.

### STL Decomposition — Analyse Temporelle
Décomposition de la série temporelle du taux de retard en tendance, saisonnalité et résidus. Détection des mois anormaux (résidus > 2σ).

### XGBoost — Modèle Prédictif
- **Régression** : Prédiction du retard moyen — MAE < 0.05 min · R² > 0.97
- **Classification** : Identification des blackspots sévères (top 25%) — F1 = 1.00

## 🛠️ Stack technique

| Outil | Usage |
|-------|-------|
| **Python** | Langage principal |
| **Pandas / NumPy** | Manipulation et nettoyage de données |
| **Folium** | Cartographie interactive (HeatMap) |
| **Plotly Express** | Graphiques interactifs |
| **Scikit-learn** | DBSCAN, Isolation Forest, preprocessing |
| **XGBoost** | Régression et classification prédictive |
| **Statsmodels (STL)** | Décomposition de séries temporelles |
| **Streamlit** | Dashboard web |

## 📁 Structure du projet

```
blackspots/
├── blackspots_infrabel.ipynb   # Notebook principal — analyse exploratoire
├── blackspots_ml.ipynb         # Extension ML — DBSCAN · IF · STL · XGBoost
├── app/
│   └── dashboard.py            # Dashboard Streamlit
├── data/
│   ├── raw/                    # Données brutes (non commitées)
│   └── clean/                  # Données nettoyées (.parquet)
├── outputs/
│   └── ml/                     # Cartes HTML + PNG générés par le notebook ML
├── requirements.txt
└── README.md
```

## 🚀 Lancement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Analyse exploratoire
jupyter notebook blackspots_infrabel.ipynb

# Extension Machine Learning
jupyter notebook blackspots_ml.ipynb

# Dashboard interactif
streamlit run app/dashboard.py
```

## 📖 Source des données

- [Open Data Infrabel — Données de ponctualité mensuelle](https://opendata.infrabel.be/explore/dataset/stiptheid-gegevens-maandelijksebestanden/)
- API v2.1 — Téléchargement automatique
- Licence : CC0 (domaine public)

## 🔍 Méthodologie complète

**Phase 1 — Ingénierie des données**
1. Téléchargement automatique via API Infrabel (19,7M lignes)
2. Exploration et audit de qualité des données
3. Nettoyage (types, doublons, valeurs aberrantes)
4. Agrégation par gare — calcul des KPIs opérationnels
5. Enrichissement géospatial (coordonnées GPS)

**Phase 2 — Visualisation**
6. HeatMap Folium pondérée par minutes perdues
7. Classement Top 50 gares les plus problématiques
8. Analyse temporelle mensuelle

**Phase 3 — Machine Learning**
9. Feature engineering (log_passages, minutes_par_passage, score_severite)
10. DBSCAN — clustering géographique des zones à risque
11. Isolation Forest — détection d'anomalies comportementales
12. STL — décomposition tendance / saisonnalité / résidus
13. XGBoost — modèle prédictif de risque de retard

## 👤 Auteur

**Tahar Guenfoud** — Data Analyst & Data Scientist
- 🌐 [Portfolio](https://proftg.github.io/portfolio)
- 💼 [LinkedIn](https://linkedin.com/in/tahar-guenfoud)
- 📧 taharguenfoud@gmail.com

---

*Projet réalisé dans le cadre du ICT Traineeship Infrabel — Data Scientist Operations.*
