# 🗺️ Cartographie des Points Noirs — Réseau Ferroviaire Belge

## Description
Projet Data Science analysant la ponctualité du réseau ferroviaire belge
à partir des données Open Data Infrabel pour identifier les gares et
tronçons les plus problématiques.

## Structure du projet
```
blackspots/
├── 01_download_data.py   # Étape 1 : Télécharger les données Infrabel
├── 02_clean_data.py      # Étape 2 : Nettoyer et agréger les données
├── 03_map.py             # Étape 3 : Générer la carte Folium interactive
├── app/
│   └── dashboard.py      # Étape 4 : Dashboard Streamlit complet
├── data/
│   ├── raw/              # Données brutes téléchargées
│   └── clean/            # Données nettoyées et agrégées
├── requirements.txt
└── README.md
```

## Lancement (dans l'ordre)
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Étape 1 : Télécharger les données
python 01_download_data.py

# Étape 2 : Nettoyer les données
python 02_clean_data.py

# Étape 3 : Générer la carte
python 03_map.py

# Étape 4 : Lancer le dashboard
streamlit run app/dashboard.py
```

## Source des données
- [Open Data Infrabel — Ponctualité mensuelle](https://opendata.infrabel.be/explore/dataset/stiptheid-gegevens-maandelijksebestanden/)

## Stack technique
- Python, Pandas, Folium, Plotly, Streamlit
