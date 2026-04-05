# =============================================================================
# app/dashboard.py — Blackspots — Points Noirs Réseau Ferroviaire Belge
# Lancement : python3 -m streamlit run app/dashboard.py
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Blackspots — Réseau Ferroviaire Belge",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main > div { padding-top: 1rem; }
    .stApp { background-color: #0a0a14; }
    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px; padding: 20px; border: 1px solid #2a2a4a;
        text-align: center; margin-bottom: 12px;
    }
    .kpi-card .kpi-label { color: #8892b0; font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .kpi-card .kpi-value { color: #e6f1ff; font-size: 2rem; font-weight: 700; line-height: 1; }
    .kpi-card .kpi-sub   { color: #64ffda; font-size: 0.85rem; margin-top: 8px; }
    .kpi-card.danger  { border-left: 4px solid #e74c3c; }
    .kpi-card.warning { border-left: 4px solid #f39c12; }
    .kpi-card.success { border-left: 4px solid #2ecc71; }
    .kpi-card.info    { border-left: 4px solid #3498db; }
    .section-title { color: #e6f1ff; font-size: 1.1rem; font-weight: 600; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #2a2a4a; }
    div[data-testid="stSidebar"] { background: #0f0f1a; border-right: 1px solid #2a2a4a; }
    h1, h2, h3 { color: #e6f1ff !important; }
    .stPlotlyChart { border-radius: 12px; overflow: hidden; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
    font={"color": "#e6f1ff", "family": "Inter"},
    xaxis=dict(gridcolor="#2a2a4a", zerolinecolor="#2a2a4a"),
)

def chart_layout_with_yaxis(**extra_yaxis):
    """Return CHART_LAYOUT with merged yaxis options."""
    yaxis = dict(gridcolor="#2a2a4a", zerolinecolor="#2a2a4a", **extra_yaxis)
    return {**CHART_LAYOUT, "yaxis": yaxis}

STATION_COORDS = {
    "BRUSSELS CENTRAL": (50.8453, 4.3571), "BRUSSEL CENTRAAL": (50.8453, 4.3571),
    "BRUSSELS MIDI": (50.8355, 4.3364), "BRUXELLES MIDI": (50.8355, 4.3364),
    "BRUSSELS NORTH": (50.8597, 4.3609), "BRUXELLES NORD": (50.8597, 4.3609),
    "BRUSSELS AIRPORT - ZAVENTEM": (50.8979, 4.4844),
    "GENT SINT PIETERS": (51.0359, 3.7107), "GHENT SINT PIETERS": (51.0359, 3.7107),
    "ANTWERP CENTRAL": (51.2172, 4.4211), "ANTWERPEN CENTRAAL": (51.2172, 4.4211),
    "LIEGE GUILLEMINS": (50.6246, 5.5667), "LUIK GUILLEMINS": (50.6246, 5.5667),
    "CHARLEROI CENTRAL": (50.4047, 4.4386), "CHARLEROI CENTRAAL": (50.4047, 4.4386),
    "BRUGES": (51.1972, 3.2168), "BRUGGE": (51.1972, 3.2168),
    "LEUVEN": (50.8823, 4.7159), "NAMUR": (50.4688, 4.8622), "NAMEN": (50.4688, 4.8622),
    "MONS": (50.4539, 3.9425), "BERGEN": (50.4539, 3.9425),
    "MECHELEN": (51.0176, 4.4828), "HASSELT": (50.9308, 5.3276),
    "KORTRIJK": (50.8245, 3.2645), "OSTEND": (51.2282, 2.9258), "OOSTENDE": (51.2282, 2.9258),
    "AALST": (50.9368, 4.0384), "SCHAERBEEK": (50.8671, 4.3836),
    "VILVOORDE": (50.9295, 4.4285), "KORTENBERG": (50.8755, 4.5450),
    "NOSSEGEM": (50.8852, 4.5027), "DENDERMONDE": (51.0261, 4.1005),
    "SINT NIKLAAS": (51.1567, 4.1336), "SINT-NIKLAAS": (51.1567, 4.1336),
    "TURNHOUT": (51.3227, 4.9478), "GENK": (50.9647, 5.5019),
    "ROESELARE": (50.9442, 3.1227), "ARLON": (49.6838, 5.8147),
    "OTTIGNIES": (50.6697, 4.5681), "WAVRE": (50.7175, 4.6033),
    "WATERLOO": (50.7176, 4.3994), "GENT DAMPOORT": (51.0530, 3.7368),
    "LIBRAMONT": (49.9203, 5.3775), "DENDERLEEUW": (50.8964, 4.0828),
}

SAMPLE_SIZE = 500_000


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    candidates = [
        "data/clean/ponctualite_clean.csv",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/clean/ponctualite_clean.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            df = pd.read_csv(path, encoding="utf-8-sig", nrows=SAMPLE_SIZE,
                             dtype={"mois": str})  # prevent mois from being parsed as datetime
            if "datdep" in df.columns:
                df["date"] = pd.to_datetime(df["datdep"], format="%d%b%Y", errors="coerce")
            df["delay_arr"] = pd.to_numeric(df.get("delay_arr", np.nan), errors="coerce")
            df["delay_dep"] = pd.to_numeric(df.get("delay_dep", np.nan), errors="coerce")
            # Filter outliers: delays > 180 min are cancelled trains or data errors
            df = df[df["delay_arr"].between(-30, 180)]
            return df
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def compute_station_stats(df):
    stats = (
        df.groupby("ptcar_lg_nm_nl")
        .agg(
            retard_moyen=("delay_arr", "mean"),
            retard_median=("delay_arr", "median"),
            retard_max=("delay_arr", "max"),
            nb_trains=("delay_arr", "count"),
            pct_en_retard=("delay_arr", lambda x: (x > 5).mean() * 100),
        )
        .round(1).reset_index()
        .rename(columns={"ptcar_lg_nm_nl": "gare"})
        .sort_values("retard_moyen", ascending=False)
    )
    def get_coords(name):
        key = name.upper().replace("-", " ").strip()
        return STATION_COORDS.get(key, (None, None))
    stats["lat"] = stats["gare"].apply(lambda x: get_coords(x)[0])
    stats["lon"] = stats["gare"].apply(lambda x: get_coords(x)[1])
    return stats


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
    <div>
        <h1 style="margin:0;color:#e6f1ff;font-size:1.8rem;">🗺️ Blackspots — Points Noirs Ferroviaires</h1>
        <p style="margin:4px 0 0 0;color:#8892b0;font-size:0.9rem;">
            Cartographie des gares à retards chroniques | Open Data Infrabel | Réseau belge
        </p>
    </div>
    <div style="text-align:right;">
        <div style="color:#8892b0;font-size:0.75rem;">{datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="color:#64ffda;font-weight:600;margin-bottom:16px;">Filtres</div>', unsafe_allow_html=True)
    seuil_retard = st.slider("Retard minimum (min)", 0, 60, 5)
    nb_top = st.slider("Nombre de gares", 5, 50, 15)
    st.divider()
    st.caption(f"Données : {SAMPLE_SIZE:,} lignes chargées")
    st.caption("Source : Open Data Infrabel")

with st.spinner("Chargement des données..."):
    df = load_data()

if df is None:
    st.error("Données introuvables. Lance d'abord `python 01_download_data.py` puis `python 02_clean_data.py`")
    st.stop()

station_stats = compute_station_stats(df)
df_filtered = station_stats[station_stats["retard_moyen"] >= seuil_retard]

# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">📊 Indicateurs Clés</div>', unsafe_allow_html=True)
worst_station = station_stats.iloc[0]["gare"] if not station_stats.empty else "N/A"
worst_delay = station_stats.iloc[0]["retard_moyen"] if not station_stats.empty else 0
pct_en_retard = (df["delay_arr"] > 5).mean() * 100

col1, col2, col3, col4, col5 = st.columns(5)
for col, label, value, sub, cls in [
    (col1, "Trains analysés",        f"{len(df):,}",                      f"{SAMPLE_SIZE/1_000_000:.1f}M dataset", "info"),
    (col2, "Gares analysées",        f"{station_stats['gare'].nunique()}", "réseau belge",                         "info"),
    (col3, "Retard moyen global",    f"{df['delay_arr'].mean():.1f} min",  "arrivée",                              "warning"),
    (col4, "Trains en retard >5min", f"{pct_en_retard:.1f}%",             "du trafic",                            "danger"),
    (col5, "Pire gare",              worst_station[:18],                   f"{worst_delay:.1f} min moy.",          "danger"),
]:
    with col:
        st.markdown(
            f'<div class="kpi-card {cls}"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Carte", "🏆 Top Gares", "📈 Tendance", "📋 Données"])

with tab1:
    st.markdown('<div class="section-title">Carte des points noirs — Intensité des retards</div>', unsafe_allow_html=True)
    df_map = df_filtered.dropna(subset=["lat", "lon"])
    if not df_map.empty:
        fig_map = px.scatter_map(
            df_map, lat="lat", lon="lon",
            color="retard_moyen", size="retard_moyen", size_max=30,
            color_continuous_scale="RdYlGn_r",
            hover_name="gare",
            hover_data={"retard_moyen": ":.1f", "nb_trains": ":,", "pct_en_retard": ":.1f", "lat": False, "lon": False},
            labels={"retard_moyen": "Retard moy (min)", "nb_trains": "Nb trains", "pct_en_retard": "% en retard"},
            zoom=7, center={"lat": 50.65, "lon": 4.50},
        )
        fig_map.update_layout(
            map_style="carto-darkmatter",
            margin={"l": 0, "r": 0, "t": 0, "b": 0}, height=520,
            coloraxis_colorbar=dict(title=dict(text="Retard (min)", font={"color": "#e6f1ff"}), tickfont={"color": "#e6f1ff"}),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(f"{len(df_map)} gares affichées | retard moyen >= {seuil_retard} min")
    else:
        st.info("Aucune gare avec coordonnées GPS pour ces filtres.")

with tab2:
    st.markdown('<div class="section-title">Top gares les plus problématiques</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        top = station_stats.head(nb_top).copy()
        top["gare_short"] = top["gare"].str[:25]
        fig = px.bar(top, x="retard_moyen", y="gare_short", orientation="h",
                     color="retard_moyen", color_continuous_scale="RdYlGn_r", text="retard_moyen",
                     labels={"retard_moyen": "Retard moyen (min)", "gare_short": ""},
                     title=f"Top {nb_top} — Retard moyen arrivée")
        fig.update_traces(texttemplate="%{text:.1f}m", textposition="outside")
        fig.update_layout(height=500, coloraxis_showscale=False, **chart_layout_with_yaxis(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)
    with col_right:
        top2 = station_stats.sort_values("pct_en_retard", ascending=False).head(nb_top).copy()
        top2["gare_short"] = top2["gare"].str[:25]
        fig2 = px.bar(top2, x="pct_en_retard", y="gare_short", orientation="h",
                      color="pct_en_retard", color_continuous_scale="RdYlGn_r", text="pct_en_retard",
                      labels={"pct_en_retard": "% trains en retard >5min", "gare_short": ""},
                      title=f"Top {nb_top} — % trains en retard")
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(height=500, coloraxis_showscale=False, **chart_layout_with_yaxis(categoryorder="total ascending"))
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">Evolution temporelle des retards</div>', unsafe_allow_html=True)
    if "date" in df.columns:
        df_trend = df.dropna(subset=["date", "delay_arr"]).groupby("date")["delay_arr"].mean().reset_index()
        df_trend.columns = ["date", "retard_moyen"]
        fig3 = px.line(df_trend, x="date", y="retard_moyen",
                       title="Evolution du retard moyen journalier",
                       labels={"retard_moyen": "Retard moyen (min)", "date": "Date"})
        fig3.update_traces(line_color="#e74c3c", line_width=2)
        fig3.update_layout(height=350, **chart_layout_with_yaxis())
        st.plotly_chart(fig3, use_container_width=True)
        if "mois" in df.columns:
            df_mois = df.dropna(subset=["mois", "delay_arr"]).groupby("mois")["delay_arr"].mean().reset_index()
            df_mois.columns = ["mois", "retard_moyen"]
            fig4 = px.bar(df_mois.sort_values("mois"), x="mois", y="retard_moyen",
                          color="retard_moyen", color_continuous_scale="RdYlGn_r", text="retard_moyen",
                          title="Retard moyen par mois",
                          labels={"mois": "Mois", "retard_moyen": "Retard moyen (min)"})
            fig4.update_traces(texttemplate="%{text:.1f}m", textposition="outside")
            fig4.update_layout(height=350, coloraxis_showscale=False, **chart_layout_with_yaxis())
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Colonne date non disponible.")

with tab4:
    st.markdown('<div class="section-title">Données complètes par gare</div>', unsafe_allow_html=True)
    display = station_stats[["gare", "retard_moyen", "retard_median", "retard_max", "nb_trains", "pct_en_retard"]].copy()
    display.columns = ["Gare", "Retard moy (min)", "Médian", "Max", "Nb trains", "% en retard"]
    st.dataframe(display, use_container_width=True, height=500)
    st.caption(f"{len(display)} gares | {len(df):,} trains analysés")

st.markdown(
    f'<div style="text-align:center;color:#8892b0;font-size:0.8rem;padding:20px 0;">'
    f'Blackspots Ferroviaires Belges | Open Data Infrabel | Tahar Guenfoud | {datetime.now().strftime("%d/%m/%Y")}'
    f'</div>', unsafe_allow_html=True,
)
