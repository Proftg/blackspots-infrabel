# 🗺️ Cartographie des Points Noirs — Réseau Ferroviaire Belge

Analyse de **22+ millions d'enregistrements** de données Open Data Infrabel pour identifier les gares et tronçons du réseau belge les plus problématiques en termes de ponctualité.

## 🎯 Objectif

Transformer des données brutes de ponctualité ferroviaire en **insights actionnables** pour prioriser les investissements infrastructure et améliorer la qualité de service.

## 📊 Résultats

- **12 mois** de données analysées (2025-01 → 2026-02)
- **22,6M+** d'enregistrements traités
- **Carte interactive** des points noirs avec heatmaps
- **Top 15** des gares les plus problématiques
- **Analyse temporelle** des tendances de retard

## 🛠️ Stack technique

| Outil | Usage |
|-------|-------|
| **Python** | Langage principal |
| **Pandas** | Manipulation et nettoyage de données |
| **Folium** | Cartographie interactive (HeatMap) |
| **Plotly** | Graphiques interactifs |
| **Streamlit** | Dashboard web |
| **Requests** | API REST — téléchargement automatique |

## 📁 Structure du projet

```
blackspots/
├── blackspots_infrabel.ipynb   # Notebook principal (analyse complète)
├── app/
│   └── dashboard.py            # Dashboard Streamlit
├── data/
│   ├── raw/                    # Données brutes (non commitées)
│   └── clean/                  # Données nettoyées
├── requirements.txt
└── README.md
```

## 🚀 Lancement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le notebook
jupyter notebook blackspots_infrabel.ipynb

# Ou lancer le dashboard
streamlit run app/dashboard.py
```

## 📖 Source des données

- [Open Data Infrabel — Ponctualité mensuelle](https://opendata.infrabel.be/explore/dataset/stiptheid-gegevens-maandelijksebestanden/)
- API v2.1 — Téléchargement automatique des 12 derniers mois
- Licence : CC0 (Open Data)

## 🔍 Méthodologie

1. **Téléchargement** — Récupération automatique via API Infrabel (22M+ lignes)
2. **Exploration** — Analyse structure, types, valeurs manquantes
3. **Nettoyage** — Conversion types, suppression doublons, normalisation
4. **Agrégation** — Groupby gare avec calcul retard moyen
5. **Géolocalisation** — Coordonnées GPS des principales gares
6. **Visualisation** — Carte Folium + graphiques Plotly
7. **Insights** — Conclusions et recommandations

## 👤 Auteur

**Tahar Guenfoud** — Data Analyst & Data Scientist
- 🌐 [Portfolio](https://proftg.github.io/portfolio)
- 💼 [LinkedIn](https://linkedin.com/in/tahar-guenfoud)
- 📧 taharguenfoud@gmail.com

---

*Projet réalisé dans le cadre d'une candidature au ICT Traineeship d'Infrabel.*
