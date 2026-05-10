import streamlit as st
import pandas as pd

# Exportation au format Excel pour charger l'ensemble du classeur
url = "https://docs.google.com/spreadsheets/d/1L2tPAY-SjzQCHeT7v9VL_qsgQmV90kz21M1lql9KvN8/export?format=xlsx"

@st.cache_data
def load_data():
    return pd.ExcelFile(url)

xls = load_data()

# Indicateurs basés sur l'onglet principal
df_main = pd.read_excel(xls, sheet_name="Réponses au formulaire")
df_main.columns = df_main.columns.str.strip()

def get_col(df, name):
    for col in df.columns:
        if col.lower() == name.lower():
            return col
    return name

col_email = get_col(df_main, "Adresse e-mail")
col_raison = get_col(df_main, "RAISON SOCIALE")
col_nature = get_col(df_main, "Nature d'impôt")
col_centre = get_col(df_main, "Centre Fiscal")

st.title("Indicateurs Administratifs")

total_saisies = len(df_main)
total_raisons = df_main[col_raison].nunique() if col_raison in df_main.columns else 0
total_agents = df_main[col_email].nunique() if col_email in df_main.columns else 0
total_centres = df_main[col_centre].nunique() if col_centre in df_main.columns else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Saisies", total_saisies)
c2.metric("Entreprises Uniques", total_raisons)
c3.metric("Agents", total_agents)
c4.metric("Centres Fiscaux", total_centres)

st.divider()

st.subheader("Détail par Nature d'impôt")
if col_nature in df_main.columns:
    repartition = df_main[col_nature].value_counts().reset_index()
    repartition.columns = ["Nature d'impôt", "Quantité"]
    st.dataframe(repartition, hide_index=True)

st.divider()

# Section dynamique pour les autres onglets
st.subheader("Données Brutes (Autres onglets)")
autres_onglets = [onglet for onglet in xls.sheet_names if onglet != "Réponses au formulaire"]

if autres_onglets:
    onglet_choisi = st.selectbox("Sélectionner un onglet à visualiser", autres_onglets)
    df_autre = pd.read_excel(xls, sheet_name=onglet_choisi)
    st.dataframe(df_autre)
else:
    st.info("Aucun autre onglet détecté dans le fichier.")
