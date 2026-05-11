import streamlit as st
import pandas as pd

# Configuration de la page
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

    st.title("📊 Suivi Administratif des Saisies Fiscales")
    st.markdown("---")

    # Indicateurs
    total_saisies = len(df_main)
    total_ninea_uniques = pd.concat([df_main[col] for col in cols_ninea]).dropna().nunique() if cols_ninea else 0
    total_agents = df_main[col_email].nunique() if col_email in df_main.columns else 0
    total_centres = df_main[col_centre].nunique() if col_centre in df_main.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📝 Total Saisies", total_saisies)
    c2.metric("🏢 NINEA Uniques", total_ninea_uniques)
    c3.metric("👤 Agents", total_agents)
    c4.metric("📍 Centres Fiscaux", total_centres)

    st.write("<br>", unsafe_allow_html=True)

    # Visualisation
    col_graph, col_list = st.columns([2, 1])

    with col_graph:
        st.subheader("📈 Répartition par Nature d'impôt")
        if col_nature in df_main.columns:
            repartition = df_main[col_nature].value_counts().reset_index()
            repartition.columns = ["Nature", "Quantité"]
            st.bar_chart(data=repartition, x="Nature", y="Quantité", use_container_width=True)

    with col_list:
        st.subheader("📍 Saisies par Centre Fiscal")
        if col_centre in df_main.columns:
            # Calcul du nombre de lignes par centre
            df_centres = df_main[col_centre].value_counts().reset_index()
            df_centres.columns = ["Centre", "Nombre de Saisies"]
            st.dataframe(df_centres, hide_index=True, use_container_width=True)

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
    st.error("Onglet introuvable.")
