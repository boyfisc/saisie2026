import streamlit as st
import pandas as pd

# 1. Configuration large pour occuper tout l'écran
st.set_page_config(page_title="Dashboard Saisies", layout="wide")

url = "https://docs.google.com/spreadsheets/d/1L2tPAY-SjzQCHeT7v9VL_qsgQmV90kz21M1lql9KvN8/export?format=xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(url, sheet_name=None)

all_sheets = load_data()
df_main = all_sheets.get("Réponses au formulaire")

if df_main is not None:
    df_main.columns = df_main.columns.str.strip()

    def get_col(df, name):
        for col in df.columns:
            if col.lower() == name.lower():
                return col
        return name

    col_email = get_col(df_main, "Adresse e-mail")
    col_nature = get_col(df_main, "Nature d'impôt")
    col_centre = get_col(df_main, "Centre Fiscal")
    cols_ninea = [col for col in df_main.columns if 'ninea' in col.lower()]

    st.title("📊 Dashboard des Saisies Fiscales")
    st.markdown("---")

    # Indicateurs (KPIs)
    total_saisies = len(df_main)
    total_ninea_uniques = pd.concat([df_main[col] for col in cols_ninea]).dropna().nunique() if cols_ninea else 0
    total_agents = df_main[col_email].nunique() if col_email in df_main.columns else 0
    total_centres = df_main[col_centre].nunique() if col_centre in df_main.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📝 Total Saisies", total_saisies)
    c2.metric("🏢 NINEA Uniques", total_ninea_uniques)
    c3.metric("👤 Agents Actifs", total_agents)
    c4.metric("📍 Centres Fiscaux", total_centres)

    st.write("<br>", unsafe_allow_html=True)

    # Section des Tableaux Numériques (Divisions élargies en 2 colonnes)
    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        st.subheader("🔢 Synthèse par Nature d'impôt")
        if col_nature in df_main.columns:
            # Transformation du graphique en tableau numérique
            rep_nature = df_main[col_nature].value_counts().reset_index()
            rep_nature.columns = ["Nature d'impôt", "Volume"]
            rep_nature["Part (%)"] = (rep_nature["Volume"] / total_saisies * 100).round(2)
            st.dataframe(rep_nature, hide_index=True, use_container_width=True)

    with col_droite:
        st.subheader("📍 Synthèse par Centre Fiscal")
        if col_centre in df_main.columns:
            rep_centre = df_main[col_centre].value_counts().reset_index()
            rep_centre.columns = ["Centre Fiscal", "Volume"]
            rep_centre["Part (%)"] = (rep_centre["Volume"] / total_saisies * 100).round(2)
            st.dataframe(rep_centre, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("🗂️ Exploration des Données")
    
    tab1, tab2 = st.tabs(["📋 Réponses au formulaire", "📁 Autres onglets"])
    
    with tab1:
        st.dataframe(df_main, use_container_width=True, height=400)
    with tab2:
        autres = [o for o in all_sheets.keys() if o != "Réponses au formulaire"]
        if autres:
            choix = st.selectbox("Sélectionnez l'onglet :", autres)
            st.dataframe(all_sheets[choix], use_container_width=True, height=400)
else:
    st.error("Impossible de charger l'onglet principal.")
