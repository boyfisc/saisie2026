import streamlit as st
import pandas as pd

# 1. Configuration de la page (Doit TOUJOURS être la première commande Streamlit)
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

    # EN-TÊTE
    st.title("📊 Suivi Administratif des Saisies Fiscales")
    st.markdown("---")

    # CALCULS
    total_saisies = len(df_main)
    total_ninea_uniques = pd.concat([df_main[col] for col in cols_ninea]).dropna().nunique() if cols_ninea else 0
    total_agents = df_main[col_email].nunique() if col_email in df_main.columns else 0
    
    if col_centre in df_main.columns:
        centres_uniques = df_main[col_centre].dropna().unique()
        total_centres = len(centres_uniques)
    else:
        centres_uniques = []
        total_centres = 0

    # SECTION 1 : KPIs (Indicateurs clés alignés en haut)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📝 Total Saisies", total_saisies)
    c2.metric("🏢 Entreprises Uniques (NINEA)", total_ninea_uniques)
    c3.metric("👤 Agents de Saisie", total_agents)
    c4.metric("📍 Centres Fiscaux", total_centres)

    st.write("<br>", unsafe_allow_html=True) # Espacement vertical

    # SECTION 2 : VISUALISATION (Graphique + Liste)
    col_graph, col_list = st.columns([2, 1]) # Le graphique sera deux fois plus large que la liste

    with col_graph:
        st.subheader("📈 Répartition par Nature d'impôt")
        if col_nature in df_main.columns:
            repartition = df_main[col_nature].value_counts().reset_index()
            repartition.columns = ["Nature", "Quantité"]
            # Génération d'un graphique au lieu d'un tableau
            st.bar_chart(data=repartition, x="Nature", y="Quantité", use_container_width=True)

    with col_list:
        st.subheader("📍 Centres Fiscaux Actifs")
        if total_centres > 0:
            df_centres = pd.DataFrame(centres_uniques, columns=["Nom du Centre"])
            st.dataframe(df_centres, hide_index=True, use_container_width=True)

    st.markdown("---")

    # SECTION 3 : DONNÉES BRUTES (Organisation par Onglets)
    st.subheader("🗂️ Exploration des Données")
    
    tab1, tab2 = st.tabs(["📋 Réponses au formulaire", "📁 Autres onglets (Détails)"])
    
    with tab1:
        st.dataframe(df_main, use_container_width=True, height=400)
        
    with tab2:
        autres_onglets = [onglet for onglet in all_sheets.keys() if onglet != "Réponses au formulaire"]
        if autres_onglets:
            onglet_choisi = st.selectbox("Sélectionnez l'onglet à consulter :", autres_onglets)
            st.dataframe(all_sheets[onglet_choisi], use_container_width=True, height=400)
        else:
            st.info("Aucun autre onglet détecté dans le fichier.")

else:
    st.error("L'onglet 'Réponses au formulaire' est introuvable.")
