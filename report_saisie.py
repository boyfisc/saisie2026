import streamlit as st
import pandas as pd

url = "https://docs.google.com/spreadsheets/d/1L2tPAY-SjzQCHeT7v9VL_qsgQmV90kz21M1lql9KvN8/export?format=csv"
df = pd.read_csv(url)

st.title("Indicateurs Administratifs")

# Calcul des indicateurs
total_saisies = len(df)
total_raisons_sociales = df["RAISON SOCIALE"].nunique()
total_agents = df["Adresse e-mail"].nunique()
total_centres = df["Centre Fiscal"].nunique()

# Affichage des indicateurs en colonnes
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Saisies", total_saisies)
c2.metric("Entreprises Uniques", total_raisons_sociales)
c3.metric("Agents (Emails)", total_agents)
c4.metric("Centres Fiscaux", total_centres)

st.divider()

# Répartition par nature d'impôt
st.subheader("Détail par Nature d'impôt")
repartition_impots = df["Nature d'impôt"].value_counts().reset_index()
repartition_impots.columns = ["Nature d'impôt", "Quantité"]
st.dataframe(repartition_impots, hide_index=True)

st.divider()

# Tableau de la situation globale
st.subheader("Données Brutes")
st.dataframe(df[["Horodatage", "Adresse e-mail", "NINEA", "RAISON SOCIALE", "Nature d'impôt", "Centre Fiscal"]])
