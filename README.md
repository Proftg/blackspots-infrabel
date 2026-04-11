# 🗺️ Blackspots Infrabel — Cartographie & Analyse de Ponctualité

> Analyse exploratoire de **19,7 millions d'enregistrements** Open Data Infrabel pour identifier et cartographier les gares systématiquement problématiques du réseau ferroviaire belge.

**Auteur :** Tahar Guenfoud — Data Analyst  
**Dataset :** Infrabel Open Data API · Jan 2025 – Fév 2026  
**Stack :** Python · Pandas · Folium · Plotly · Streamlit · Power BI

---

## 🎯 Objectifs

- **Cartographier** les points noirs géographiques du réseau (HeatMap interactive Folium)
- **Analyser** la ponctualité par gare, par ligne et dans le temps (14 mois de données)
- **Identifier** les gares à fort impact sur les KPIs du Contrat de Performance Infrabel
- **Visualiser** les tendances sur un dashboard interactif (Streamlit + Power BI)

---

## 📊 Chiffres clés

| Métrique | Valeur |
|----------|--------|
| Enregistrements traités | **19 730 044** passages de trains |
| Gares analysées | **500** (sur 593 — 93 sans coordonnées GPS) |
| Lignes ferroviaires | **172** |
| Période couverte | Jan 2025 → Fév 2026 (14 mois) |
| Format de sortie | HeatMap HTML · Dashboard Streamlit · Rapport Power BI |

---

## 🗺️ Cartographie — HeatMap Folium

Carte interactive des gares classées par score de ponctualité. Chaque point représente une gare belge — couleur et intensité proportionnelles au retard moyen pondéré par le volume de passages.

Les zones rouges correspondent aux bassins ferroviaires à fort impact sur les KPIs du Contrat de Performance (Bruxelles-Jonction Nord-Midi, Liège-Guillemins, Charleroi-Sud, Anvers-Central).

---

## 📈 Dashboard Streamlit

Dashboard interactif permettant d'explorer :
- Classement des gares par retard moyen, % de trains en retard, minutes perdues
- Évolution temporelle des indicateurs (filtre par gare, par ligne, par période)
- Comparaison entre bassins géographiques

```bash
cd app/
streamlit run dashboard.py
```

---

## 🛠️ Stack technique

| Outil | Usage |
|-------|-------|
| **Python 3.10** | Langage principal |
| **Pandas / NumPy** | Manipulation et nettoyage (19,7M lignes) |
| **Folium** | Cartographie interactive — HeatMap géographique |
| **Plotly Express** | Graphiques interactifs (tendances, distributions) |
| **Streamlit** | Dashboard web interactif |
| **Power BI** | Rapport KPI — Contrat de Performance Infrabel |
| **Parquet** | Format de stockage optimisé (×100 plus rapide que CSV) |

---

## 📁 Structure du projet

```
blackspots-infrabel/
├── blackspots_infrabel.ipynb   # Notebook principal — analyse exploratoire
├── blackspots_infrabel.py      # Script Python standalone
├── app/
│   └── dashboard.py            # Dashboard Streamlit
├── data/
│   ├── raw/                    # Données brutes Infrabel (non commitées — >500 MB)
│   └── clean/
│       ├── blackspots_final.parquet    # 500 gares × 10 features agrégées
│       └── ponctualite_clean.parquet  # 19,7M enregistrements nettoyés
├── outputs/
│   ├── maps/                   # Cartes HeatMap HTML (Folium)
│   └── charts/                 # Graphiques exportés (PNG)
├── requirements.txt
└── README.md
```

---

## 🚀 Lancement

```bash
pip install -r requirements.txt

# Analyse exploratoire
jupyter notebook blackspots_infrabel.ipynb

# Dashboard interactif
streamlit run app/dashboard.py
```

---

## 📦 Source des données

Données issues de l'**API Open Data Infrabel** (publique, gratuite, licence CC0) :
`https://opendata.infrabel.be/explore/dataset/stiptheid-van-de-treinen/`

Les fichiers Parquet ne sont pas committés (taille > 500 MB). Le pipeline complet de téléchargement et nettoyage est disponible dans `blackspots_infrabel.ipynb`.

---

## 🤖 Extension Machine Learning

L'analyse prédictive complète (DBSCAN · Isolation Forest · XGBoost · Stacking Ensemble · K-Fold CV) est disponible dans un dépôt dédié, orienté Data Science :

👉 **[railway-delay-ml](https://github.com/Proftg/railway-delay-ml)** — Pipeline ML complet avec validation croisée 5 folds, Pipeline sklearn anti-leakage, comparaison multi-modèles

---

## 🔗 Projets liés

- **[railway-delay-ml](https://github.com/Proftg/railway-delay-ml)** — ML pipeline : DBSCAN · IF · XGBoost · Stacking (Data Scientist)
- **[infrabel-dashboard](https://github.com/Proftg/infrabel-dashboard)** — Dashboard KPI Contrat de Performance Infrabel

---

## 👤 Auteur

**Tahar Guenfoud**  
Data Analyst | Master Data Science — UMONS 2025 | Le Wagon 2025  
📧 taharguenfoud@gmail.com · 🔗 [github.com/Proftg](https://github.com/Proftg)
