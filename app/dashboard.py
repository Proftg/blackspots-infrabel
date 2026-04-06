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
DATA_URL = "https://raw.githubusercontent.com/Proftg/blackspots-infrabel/main/data/sample.csv"

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
    yaxis = dict(gridcolor="#2a2a4a", zerolinecolor="#2a2a4a", **extra_yaxis)
    return {**CHART_LAYOUT, "yaxis": yaxis}

STATION_COORDS = {
    # Brussels
    "BRUSSEL-CENTRAAL": (50.8453, 4.3571),
    "BRUSSEL-ZUID": (50.8355, 4.3364),
    "BRUSSEL-NOORD": (50.8597, 4.3609),
    "BRUSSEL-LUXEMBURG": (50.8412, 4.3647),
    "BRUSSEL-KAPELLEKERK": (50.8463, 4.3508),
    "BRUSSEL-CONGRES": (50.8521, 4.3601),
    "SCHAARBEEK": (50.8671, 4.3836),
    "ETTERBEEK": (50.8365, 4.3881),
    # Antwerp
    "ANTWERPEN-CENTRAAL": (51.2172, 4.4211),
    "ANTWERPEN-BERCHEM": (51.1990, 4.4317),
    "ANTWERPEN-DAM": (51.2280, 4.4055),
    # Ghent
    "GENT-SINT-PIETERS": (51.0359, 3.7107),
    "GENT-DAMPOORT": (51.0530, 3.7368),
    # Liège
    "LIEGE-GUILLEMINS": (50.6246, 5.5667),
    # Charleroi
    "CHARLEROI-CENTRAL": (50.4047, 4.4386),
    "CHARLEROI-CENTRAAL": (50.4047, 4.4386),
    # Other major cities
    "BRUGGE": (51.1972, 3.2168),
    "LEUVEN": (50.8823, 4.7159),
    "NAMEN": (50.4688, 4.8622),
    "BERGEN": (50.4539, 3.9425),
    "MECHELEN": (51.0176, 4.4828),
    "MECHELEN-NEKKERSPOEL": (51.0120, 4.4750),
    "HASSELT": (50.9308, 5.3276),
    "KORTRIJK": (50.8245, 3.2645),
    "OOSTENDE": (51.2282, 2.9258),
    "AALST": (50.9368, 4.0384),
    "VILVOORDE": (50.9295, 4.4285),
    "KORTENBERG": (50.8755, 4.5450),
    "NOSSEGEM": (50.8852, 4.5027),
    "ZAVENTEM": (50.8979, 4.4844),
    "DIEGEM": (50.8933, 4.4469),
    "DENDERMONDE": (51.0261, 4.1005),
    "SINT-NIKLAAS": (51.1567, 4.1336),
    "TURNHOUT": (51.3227, 4.9478),
    "GENK": (50.9647, 5.5019),
    "ROESELARE": (50.9442, 3.1227),
    "AARLEN": (49.6838, 5.8147),
    "OTTIGNIES": (50.6697, 4.5681),
    "WAVER": (50.7175, 4.6033),
    "WATERLOO": (50.7176, 4.3994),
    "LIBRAMONT": (49.9203, 5.3775),
    "DENDERLEEUW": (50.8964, 4.0828),
    "HALLE": (50.7340, 4.2337),
    "EPPEGEM": (50.9636, 4.4667),
    "HAREN-ZUID": (50.8822, 4.3905),
    "ERPS-KWERPS": (50.8833, 4.5833),
    "VELTEM": (50.8900, 4.6167),
    "HERENT": (50.8983, 4.6833),
    "WEERDE": (50.9667, 4.5167),
    "MORTSEL": (51.1667, 4.4500),
    "DUFFEL": (51.0833, 4.5167),
    "SINT-KATELIJNE-WAVER": (51.0667, 4.5333),
}

@st.cache_data(ttl=86400, show_spinner=False)
def load_data():
    df = pd.read_csv(DATA_URL, dtype={"mois": str})
    if "datdep" in df.columns:
        df["date"] = pd.to_datetime(df["datdep"], format="%d%b%Y", errors="coerce")
    df["delay_arr"] = pd.to_numeric(df["delay_arr"], errors="coerce")
    df["delay_dep"] = pd.to_numeric(df["delay_dep"], errors="coerce")
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def compute_station_stats(df_hash):
    stats = (
        df_hash.groupby("ptcar_lg_nm_nl")
        .agg(
            retard_moyen=("delay_arr", "mean"),
            retard_median=("delay_arr", "median"),
            retard_max=("delay_arr", "max"),
            nb_trains=("delay_arr", "count"),
            pct_en_retard=("delay_arr", lambda x: (x > 5).mean() * 100),
        )
        .round(2).reset_index()
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
# Load data
# ---------------------------------------------------------------------------
with st.spinner("Chargement des données Infrabel... (première visite : ~2 min)"):
    df_raw = load_data()

if df_raw is None or df_raw.empty:
    st.error(f"Fichier introuvable : `{DATA_FILE}`")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — Point 1 : Filtres
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div style="color:#64ffda;font-weight:600;margin-bottom:16px;">Filtres</div>', unsafe_allow_html=True)

    # Filter by train service
    services_dispo = sorted(df_raw["train_serv"].dropna().unique()) if "train_serv" in df_raw.columns else []
    service_sel = st.multiselect(
        "Service",
        options=services_dispo,
        default=["SNCB/NMBS"] if "SNCB/NMBS" in services_dispo else services_dispo,
    )

    seuil_retard = st.slider("Retard minimum affiché (min)", 0, 30, 2)
    nb_top = st.slider("Nombre de gares (Top)", 5, 50, 15)

    st.divider()
    mois_dispo = sorted(df_raw["mois"].dropna().unique()) if "mois" in df_raw.columns else []
    st.caption(f"Période : {mois_dispo[0]} → {mois_dispo[-1]}" if mois_dispo else "")
    st.caption(f"{len(df_raw):,} lignes chargées | Open Data Infrabel")

# Apply filters
df = df_raw.copy()
if service_sel:
    df = df[df["train_serv"].isin(service_sel)]

# ---------------------------------------------------------------------------
# Header — Point 5 : date + période
# ---------------------------------------------------------------------------
mois_range = f"{mois_dispo[0]} → {mois_dispo[-1]}" if mois_dispo else ""
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
    <div>
        <h1 style="margin:0;color:#e6f1ff;font-size:1.8rem;">🗺️ Blackspots — Points Noirs Ferroviaires</h1>
        <p style="margin:4px 0 0 0;color:#8892b0;font-size:0.9rem;">
            Cartographie des gares à retards chroniques | Open Data Infrabel | {mois_range}
        </p>
    </div>
    <div style="text-align:right;">
        <div style="color:#8892b0;font-size:0.75rem;">Mise à jour : {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
        <div style="color:#64ffda;font-size:0.75rem;">{len(df_raw):,} passages analysés</div>
    </div>
</div>
""", unsafe_allow_html=True)

station_stats = compute_station_stats(df)
df_filtered = station_stats[station_stats["retard_moyen"] >= seuil_retard]

# ---------------------------------------------------------------------------
# KPI Cards — Point 2 : ajout "pire mois"
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">📊 Indicateurs Clés</div>', unsafe_allow_html=True)
worst_station = station_stats.iloc[0]["gare"] if not station_stats.empty else "N/A"
worst_delay = station_stats.iloc[0]["retard_moyen"] if not station_stats.empty else 0
pct_en_retard = (df["delay_arr"] > 5).mean() * 100

# Point 2 : pire mois
if "mois" in df.columns:
    worst_month = df.groupby("mois")["delay_arr"].mean().idxmax()
    worst_month_val = df.groupby("mois")["delay_arr"].mean().max()
else:
    worst_month, worst_month_val = "N/A", 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
for col, label, value, sub, cls in [
    (col1, "Trains analysés",        f"{len(df):,}",                         f"{len(df_raw)/1_000_000:.1f}M dataset",  "info"),
    (col2, "Gares analysées",        f"{station_stats['gare'].nunique()}",    "réseau belge",                            "info"),
    (col3, "Retard moyen global",    f"{df['delay_arr'].mean():.1f} min",     "arrivée",                                 "warning"),
    (col4, "Trains en retard >5min", f"{pct_en_retard:.1f}%",                "du trafic",                               "danger"),
    (col5, "Pire gare",              worst_station[:16],                      f"{worst_delay:.1f} min moy.",             "danger"),
    (col6, "Pire mois",              worst_month,                             f"{worst_month_val:.1f} min moy.",         "warning"),
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
            hover_data={"retard_moyen": ":.2f", "nb_trains": ":,", "pct_en_retard": ":.1f", "lat": False, "lon": False},
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
                      title=f"Top {nb_top} — % trains en retard >5min")
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
        # Point 4 : ligne de référence à 5 min
        fig3.add_hline(y=5, line_dash="dash", line_color="#64ffda",
                       annotation_text="Seuil 5 min", annotation_position="top right",
                       annotation_font_color="#64ffda")
        fig3.update_layout(height=380, **chart_layout_with_yaxis())
        st.plotly_chart(fig3, use_container_width=True)

        if "mois" in df.columns:
            df_mois = df.dropna(subset=["mois", "delay_arr"]).groupby("mois")["delay_arr"].mean().reset_index()
            df_mois.columns = ["mois", "retard_moyen"]
            df_mois["mois"] = df_mois["mois"].astype(str)
            df_mois = df_mois.sort_values("mois")
            fig4 = px.bar(df_mois, x="mois", y="retard_moyen",
                          color="retard_moyen", color_continuous_scale="RdYlGn_r", text="retard_moyen",
                          title="Retard moyen par mois",
                          labels={"mois": "Mois", "retard_moyen": "Retard moyen (min)"})
            fig4.update_traces(texttemplate="%{text:.1f}m", textposition="outside")
            # Point 4 : ligne de référence à 5 min sur le bar chart aussi
            fig4.add_hline(y=5, line_dash="dash", line_color="#64ffda",
                           annotation_text="Seuil 5 min", annotation_position="top right",
                           annotation_font_color="#64ffda")
            layout4 = {**chart_layout_with_yaxis(),
                       "height": 430, "coloraxis_showscale": False,
                       "xaxis": dict(type="category", tickangle=-45, gridcolor="#2a2a4a", zerolinecolor="#2a2a4a")}
            fig4.update_layout(**layout4)
            st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Colonne date non disponible.")

with tab4:
    st.markdown('<div class="section-title">Données complètes par gare</div>', unsafe_allow_html=True)
    display = station_stats[["gare", "retard_moyen", "retard_median", "retard_max", "nb_trains", "pct_en_retard"]].copy()
    display.columns = ["Gare", "Retard moy (min)", "Médian", "Max", "Nb trains", "% en retard >5min"]
    st.dataframe(display, use_container_width=True, height=500)
    st.caption(f"{len(display)} gares | {len(df):,} trains analysés")

st.markdown(
    f'<div style="text-align:center;color:#8892b0;font-size:0.8rem;padding:20px 0;">'
    f'Blackspots Ferroviaires Belges | Open Data Infrabel | Tahar Guenfoud | {datetime.now().strftime("%d/%m/%Y")}'
    f'</div>', unsafe_allow_html=True,
)
