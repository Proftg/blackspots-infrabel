# =============================================================================
# app/dashboard.py
# Objectif : Dashboard interactif Streamlit — Points Noirs Réseau Belge
# Lancement : streamlit run app/dashboard.py
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
from streamlit.components.v1 import html
import os
import sys

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Configuration de la page ---
st.set_page_config(
    page_title="Points Noirs — Réseau Ferroviaire Belge",
    page_icon="🚄",
    layout="wide"
)

# --- Chargement des données ---
@st.cache_data
def load_data():
    """Charge les données propres (avec cache Streamlit)."""
    filepath = "data/clean/ponctualite_par_gare.csv"
    if not os.path.exists(filepath):
        return None
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    return df

@st.cache_data
def load_clean_data():
    """Charge les données détaillées."""
    filepath = "data/clean/ponctualite_clean.csv"
    if not os.path.exists(filepath):
        return None
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


# ============================================================
# HEADER
# ============================================================
st.title("🗺️ Cartographie des Points Noirs")
st.subheader("Analyse de la ponctualité du réseau ferroviaire belge (Open Data Infrabel)")
st.markdown("---")


# ============================================================
# CHARGEMENT
# ============================================================
df_gare  = load_data()
df_clean = load_clean_data()

if df_gare is None:
    st.error("❌ Données introuvables. Lance d'abord : `python 01_download_data.py` puis `python 02_clean_data.py`")
    st.stop()

# Détecter la colonne de retard
retard_col = None
for col in ["retard_minutes", "taux_ponctualite"]:
    if col in df_gare.columns:
        retard_col = col
        break
if retard_col is None and len(df_gare.columns) > 1:
    retard_col = df_gare.columns[1]


# ============================================================
# KPI CARDS — ligne du haut
# ============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🚉 Gares analysées",
        value=f"{len(df_gare):,}"
    )

with col2:
    if retard_col and retard_col in df_gare.columns:
        moy = df_gare[retard_col].mean()
        st.metric(
            label=f"📊 {retard_col.replace('_',' ').title()} moyen",
            value=f"{moy:.1f}"
        )

with col3:
    if retard_col and retard_col in df_gare.columns:
        worst = df_gare.nlargest(1, retard_col).iloc[0]
        st.metric(
            label="🔴 Gare la plus problématique",
            value=str(worst.get("gare", "N/A"))[:20],
            delta=f"{worst[retard_col]:.1f}",
            delta_color="inverse"
        )

with col4:
    if df_clean is not None and "date" in df_clean.columns:
        date_min = df_clean["date"].min()
        date_max = df_clean["date"].max()
        st.metric(
            label="📅 Période couverte",
            value=f"{date_min.strftime('%m/%Y') if pd.notna(date_min) else 'N/A'}",
            delta=f"→ {date_max.strftime('%m/%Y') if pd.notna(date_max) else 'N/A'}"
        )
    else:
        st.metric(label="📅 Données", value="Chargées ✅")

st.markdown("---")


# ============================================================
# COLONNES PRINCIPALES : Carte + Top 10
# ============================================================
col_map, col_chart = st.columns([3, 2])

with col_map:
    st.subheader("🗺️ Carte interactive")

    # Charger la carte HTML si elle existe
    carte_path = "app/carte_points_noirs.html"
    if os.path.exists(carte_path):
        with open(carte_path, "r", encoding="utf-8") as f:
            carte_html = f.read()
        html(carte_html, height=500, scrolling=False)
        st.caption("💡 Lance `python 03_map.py` pour régénérer la carte")
    else:
        st.info("🔄 Carte non générée. Lance : `python 03_map.py`")

with col_chart:
    st.subheader("🏆 Top 15 des gares problématiques")

    if retard_col and retard_col in df_gare.columns:
        top15 = df_gare.nlargest(15, retard_col)[["gare", retard_col]].copy()
        top15["gare"] = top15["gare"].str[:25]  # Tronquer les noms longs

        fig = px.bar(
            top15,
            x=retard_col,
            y="gare",
            orientation="h",
            color=retard_col,
            color_continuous_scale=["green", "orange", "red"],
            title=f"Top 15 — {retard_col.replace('_', ' ').title()}",
            labels={retard_col: retard_col.replace("_", " ").title(), "gare": "Gare"}
        )
        fig.update_layout(
            height=500,
            showlegend=False,
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


# ============================================================
# TENDANCE TEMPORELLE (si données disponibles)
# ============================================================
if df_clean is not None and "date" in df_clean.columns and retard_col in df_clean.columns:
    st.subheader("📈 Évolution temporelle")

    df_trend = df_clean.groupby("date")[retard_col].mean().reset_index()
    df_trend.columns = ["date", "valeur_moyenne"]

    fig2 = px.line(
        df_trend,
        x="date",
        y="valeur_moyenne",
        title=f"Évolution du {retard_col.replace('_', ' ')} moyen dans le temps",
        labels={"valeur_moyenne": retard_col.replace("_", " ").title(), "date": "Date"},
        markers=True
    )
    fig2.update_traces(line_color="#e63946", line_width=2)
    fig2.update_layout(height=300)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")


# ============================================================
# TABLE DE DONNÉES
# ============================================================
st.subheader("📋 Données complètes par gare")

# Filtre interactif
if retard_col:
    seuil = st.slider(
        f"Filtrer — {retard_col.replace('_', ' ').title()} minimum",
        min_value=float(df_gare[retard_col].min()),
        max_value=float(df_gare[retard_col].max()),
        value=float(df_gare[retard_col].quantile(0.5))
    )
    df_filtered = df_gare[df_gare[retard_col] >= seuil]
else:
    df_filtered = df_gare

st.dataframe(
    df_filtered.sort_values(retard_col, ascending=False) if retard_col else df_filtered,
    use_container_width=True,
    height=300
)

st.caption(f"📊 {len(df_filtered)} gares affichées sur {len(df_gare)} au total")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "**Source :** [Open Data Infrabel](https://opendata.infrabel.be) | "
    "**Projet :** Portfolio Data Science — Tahar GUENFOUD | "
    "**Stack :** Python · Pandas · Folium · Plotly · Streamlit"
)
