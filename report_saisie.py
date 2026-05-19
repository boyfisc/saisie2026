"""
Dashboard Saisies Fiscales - DGID/DSI
Version améliorée : filtres dynamiques, vues croisées, détection d'anomalies.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Saisies Fiscales",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

URL = "https://docs.google.com/spreadsheets/d/1L2tPAY-SjzQCHeT7v9VL_qsgQmV90kz21M1lql9KvN8/export?format=xlsx"

# Liste de référence des centres fiscaux attendus (à adapter à votre nomenclature)
# Si un centre est attendu mais absent des saisies, il sera affiché à 0.
CENTRES_REFERENCE = [
    "DGE", "CGE", "CPR",
    "DAKAR PLATEAU 1", "DAKAR PLATEAU 2", "DAKAR LIBERTE",
    "DAKAR MEDINA", "GRAND DAKAR", "PIKINE", "GUEDIAWAYE",
    "RUFISQUE", "THIES", "MBOUR", "SAINT-LOUIS", "LOUGA",
    "DIOURBEL", "KAOLACK", "FATICK", "KAFFRINE", "TAMBACOUNDA",
    "KEDOUGOU", "KOLDA", "SEDHIOU", "ZIGUINCHOR", "MATAM",
]

# ─────────────────────────────────────────────────────────────
# Chargement des données (avec cache pour la performance)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="Chargement des données…")
def load_data():
    """Charge le classeur Excel depuis Google Sheets."""
    return pd.read_excel(URL, sheet_name=None)


def get_col(df: pd.DataFrame, name: str) -> str:
    """Retourne le nom exact d'une colonne (insensible à la casse)."""
    for col in df.columns:
        if col.lower() == name.lower():
            return col
    return name


# ─────────────────────────────────────────────────────────────
# Chargement
# ─────────────────────────────────────────────────────────────
try:
    all_sheets = load_data()
except Exception as e:
    st.error(f"❌ Impossible de charger les données : {e}")
    st.stop()

df_main = all_sheets.get("Réponses au formulaire")
if df_main is None or df_main.empty:
    st.error("Impossible de charger l'onglet 'Réponses au formulaire'.")
    st.stop()

df_main.columns = df_main.columns.str.strip()

col_horodateur = get_col(df_main, "Horodateur")
col_email = get_col(df_main, "Adresse e-mail")
col_nature = get_col(df_main, "Nature d'impôt")
col_centre = get_col(df_main, "CENTRE FISCAL")
cols_ninea = [c for c in df_main.columns if "ninea" in c.lower()]

# Parsing de la date
if col_horodateur in df_main.columns:
    df_main["_date"] = pd.to_datetime(
        df_main[col_horodateur], errors="coerce", dayfirst=True
    )
else:
    df_main["_date"] = pd.NaT

# ─────────────────────────────────────────────────────────────
# Sidebar - Filtres
# ─────────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filtres")

# Filtre centres
centres_dispo = sorted(df_main[col_centre].dropna().unique().tolist()) if col_centre in df_main.columns else []
centres_selection = st.sidebar.multiselect(
    "Centres fiscaux",
    options=centres_dispo,
    default=centres_dispo,
    help="Filtrer les saisies par centre fiscal.",
)

# Filtre nature d'impôt
natures_dispo = sorted(df_main[col_nature].dropna().unique().tolist()) if col_nature in df_main.columns else []
natures_selection = st.sidebar.multiselect(
    "Nature d'impôt",
    options=natures_dispo,
    default=natures_dispo,
)

# Filtre période
if df_main["_date"].notna().any():
    date_min = df_main["_date"].min().date()
    date_max = df_main["_date"].max().date()
    periode = st.sidebar.date_input(
        "Période",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )
else:
    periode = None

# Option : afficher les centres de référence absents
show_centres_absents = st.sidebar.checkbox(
    "Afficher les centres de référence sans saisie",
    value=True,
    help="Inclut les centres attendus mais qui n'ont aucune saisie (volume = 0).",
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()

# ─────────────────────────────────────────────────────────────
# Application des filtres
# ─────────────────────────────────────────────────────────────
df = df_main.copy()
if centres_selection:
    df = df[df[col_centre].isin(centres_selection)]
if natures_selection:
    df = df[df[col_nature].isin(natures_selection)]
if periode and isinstance(periode, tuple) and len(periode) == 2:
    d1, d2 = periode
    df = df[(df["_date"].dt.date >= d1) & (df["_date"].dt.date <= d2)]

# ─────────────────────────────────────────────────────────────
# En-tête
# ─────────────────────────────────────────────────────────────
st.title("📊 Dashboard des Saisies Fiscales")
st.caption(f"Dernière actualisation : {datetime.now().strftime('%d/%m/%Y %H:%M')}  •  {len(df)} saisies après filtrage")
st.markdown("---")

# ─────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────
total_saisies = len(df)
total_ninea_uniques = (
    pd.concat([df[c] for c in cols_ninea]).dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique()
    if cols_ninea else 0
)
total_agents = df[col_email].nunique() if col_email in df.columns else 0
total_centres = df[col_centre].nunique() if col_centre in df.columns else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("📝 Total Saisies", f"{total_saisies:,}".replace(",", " "))
c2.metric("🏢 NINEA Uniques", f"{total_ninea_uniques:,}".replace(",", " "))
c3.metric("👤 Agents Actifs", total_agents)
c4.metric("📍 Centres Actifs", total_centres)

st.markdown("")

# ─────────────────────────────────────────────────────────────
# Synthèses par Nature et par Centre
# ─────────────────────────────────────────────────────────────
col_g, col_d = st.columns(2)

with col_g:
    st.subheader("🔢 Répartition par Nature d'impôt")
    if col_nature in df.columns and total_saisies > 0:
        rep_nature = df[col_nature].value_counts(dropna=False).reset_index()
        rep_nature.columns = ["Nature d'impôt", "Volume"]
        rep_nature["Part (%)"] = (rep_nature["Volume"] / total_saisies * 100).round(2)
        st.dataframe(rep_nature, hide_index=True, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_d:
    st.subheader("📍 Répartition par Centre Fiscal")
    if col_centre in df.columns:
        rep_centre = df[col_centre].value_counts(dropna=False).reset_index()
        rep_centre.columns = ["Centre Fiscal", "Volume"]

        # Ajout des centres de référence absents
        if show_centres_absents:
            centres_presents = set(rep_centre["Centre Fiscal"].astype(str).str.upper())
            absents = [
                {"Centre Fiscal": c, "Volume": 0}
                for c in CENTRES_REFERENCE
                if c.upper() not in centres_presents
            ]
            if absents:
                rep_centre = pd.concat(
                    [rep_centre, pd.DataFrame(absents)], ignore_index=True
                )

        rep_centre["Part (%)"] = (
            rep_centre["Volume"] / total_saisies * 100 if total_saisies else 0
        ).round(2)
        rep_centre = rep_centre.sort_values("Volume", ascending=False).reset_index(drop=True)
        st.dataframe(rep_centre, hide_index=True, use_container_width=True, height=320)
    else:
        st.info("Aucune donnée.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Tableau croisé Centre × Nature d'impôt
# ─────────────────────────────────────────────────────────────
st.subheader("🧮 Tableau croisé : Centre Fiscal × Nature d'impôt")
if col_centre in df.columns and col_nature in df.columns and not df.empty:
    pivot = pd.crosstab(
        df[col_centre],
        df[col_nature],
        margins=True,
        margins_name="TOTAL",
    )
    st.dataframe(pivot, use_container_width=True)
else:
    st.info("Données insuffisantes pour le tableau croisé.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Top agents et évolution
# ─────────────────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("👤 Top Agents (volume de saisies)")
    if col_email in df.columns and not df.empty:
        top_agents = df[col_email].value_counts().head(10).reset_index()
        top_agents.columns = ["Agent", "Saisies"]
        st.dataframe(top_agents, hide_index=True, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_b:
    st.subheader("📈 Évolution quotidienne des saisies")
    if df["_date"].notna().any():
        evo = df.dropna(subset=["_date"]).copy()
        evo["jour"] = evo["_date"].dt.date
        serie = evo.groupby("jour").size()
        st.bar_chart(serie, use_container_width=True)
    else:
        st.info("Aucune donnée temporelle.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Détection d'anomalies
# ─────────────────────────────────────────────────────────────
st.subheader("⚠️ Contrôles de cohérence")

col_x, col_y, col_z = st.columns(3)

# Saisies sans NINEA
saisies_sans_ninea = 0
if cols_ninea:
    mask_sans_ninea = df[cols_ninea].apply(
        lambda r: r.dropna().astype(str).str.strip().replace("", pd.NA).dropna().empty,
        axis=1,
    )
    saisies_sans_ninea = int(mask_sans_ninea.sum())
col_x.metric("Saisies sans NINEA", saisies_sans_ninea)

# Doublons potentiels (même NINEA + même nature)
doublons = 0
if cols_ninea and col_nature in df.columns:
    df_check = df.copy()
    df_check["_ninea_first"] = (
        df_check[cols_ninea].bfill(axis=1).iloc[:, 0].astype(str).str.strip()
    )
    df_check = df_check[df_check["_ninea_first"].notna() & (df_check["_ninea_first"] != "")]
    dup = df_check.duplicated(subset=["_ninea_first", col_nature], keep=False)
    doublons = int(dup.sum())
col_y.metric("Doublons potentiels (NINEA+Nature)", doublons)

# Centres sans aucune saisie sur la période
centres_inactifs = 0
if show_centres_absents and col_centre in df.columns:
    presents = set(df[col_centre].dropna().astype(str).str.upper())
    centres_inactifs = sum(1 for c in CENTRES_REFERENCE if c.upper() not in presents)
col_z.metric("Centres de réf. inactifs", centres_inactifs)

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Exploration des données
# ─────────────────────────────────────────────────────────────
st.subheader("🗂️ Exploration des Données")

tab1, tab2 = st.tabs(["📋 Réponses filtrées", "📁 Autres onglets"])

with tab1:
    # Recherche textuelle
    recherche = st.text_input("🔍 Recherche (sur toutes les colonnes)", "")
    df_view = df.drop(columns=["_date"], errors="ignore")
    if recherche:
        mask = df_view.astype(str).apply(
            lambda r: r.str.contains(recherche, case=False, na=False)
        ).any(axis=1)
        df_view = df_view[mask]
        st.caption(f"{len(df_view)} ligne(s) correspondante(s)")

    st.dataframe(df_view, use_container_width=True, height=400)

    # Export
    csv = df_view.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Télécharger en CSV",
        data=csv,
        file_name=f"saisies_filtrees_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )

with tab2:
    autres = [o for o in all_sheets.keys() if o != "Réponses au formulaire"]
    if autres:
        choix = st.selectbox("Sélectionnez l'onglet :", autres)
        st.dataframe(all_sheets[choix], use_container_width=True, height=400)
    else:
        st.info("Aucun autre onglet disponible.")
