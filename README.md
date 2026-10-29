# Blackspots Infrabel

Carte des gares belges où les trains arrivent le plus souvent en retard, construite sur 19,7 millions de passages issus de l'Open Data Infrabel (janvier 2025 à février 2026).

## Ce que contient le projet

- 500 gares analysées sur 593 (93 n'ont pas de coordonnées GPS) et 172 lignes.
- Une carte de chaleur Folium : couleur et intensité suivent le retard moyen, pondéré par le nombre de passages.
- Un dashboard Streamlit : classement des gares, évolution dans le temps, filtres par gare, ligne et période.
- Un notebook avec le téléchargement, le nettoyage et l'analyse.

## Lancer

```bash
pip install -r requirements.txt
jupyter notebook blackspots_infrabel.ipynb
streamlit run app/dashboard.py
```

Les fichiers Parquet (plus de 500 Mo) ne sont pas dans le dépôt : le notebook les reconstruit depuis l'[API Open Data Infrabel](https://opendata.infrabel.be/explore/dataset/stiptheid-van-de-treinen/).

## Structure

```
blackspots_infrabel.ipynb   analyse exploratoire
app/dashboard.py            dashboard Streamlit
data/clean/                 blackspots_final.parquet (500 gares x 10 features), ponctualite_clean.parquet
outputs/                    cartes HTML et graphiques
```

## Suite

Le modèle prédictif (DBSCAN, Isolation Forest, XGBoost) est dans [railway-delay-ml](https://github.com/Proftg/railway-delay-ml). Les KPI du Contrat de Performance sont dans [infrabel-dashboard](https://github.com/Proftg/infrabel-dashboard).

Tahar Guenfoud, [github.com/Proftg](https://github.com/Proftg)
