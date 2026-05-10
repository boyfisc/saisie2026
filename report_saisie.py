import streamlit as st
import pandas as pd

url = "https://docs.google.com/spreadsheets/d/1L2tPAY-SjzQCHeT7v9VL_qsgQmV90kz21M1lql9KvN8/export?format=csv"
df = pd.read_csv(url)

# Nettoyage des noms de colonnes pour éviter les espaces invisibles
df.columns = df.columns.str.strip()

# Fonction pour trouver le nom exact (insensible à la casse)
def get_col(name):
    for col in df.columns:
        if col.lower() == name.lower():
            return col
    return name

col_email = get_col("Adresse e-mail")
col_raison = get_col("RAISON SOCIALE")
col_nature = get_col("Nature d'impôt")
col_centre = get_col("Centre Fiscal")
col_ninea = get_col("NINEA")

st.title("Indicateurs Administratifs")

# Calcul avec vérification d'existence des colonnes
total_saisies = len(df)
total_raisons = df[col_raison].nunique() if col_raison in df.columns else 0
total_agents = df[col_email].nunique() if col_email in df.columns else 0
total_centres = df[col_centre].nunique() if col_centre in df.columns else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Saisies", total_saisies)
c2.metric("Entreprises Uniques", total_raisons)
c3.metric("Agents", total_agents)
c4.metric("Centres Fiscaux", total_centres)

st.divider()

st.subheader("Détail par Nature d'impôt")
if col_nature in df.columns:
    repartition = df[col_nature].value_counts().reset_index()
    repartition.columns = ["Nature d'impôt", "Quantité"]
    st.dataframe(repartition, hide_index=True)

st.divider()

st.subheader("Données Brutes")
colonnes_a_afficher = [c for c in ["Horodatage", col_email, col_ninea, col_raison, col_nature, col_centre] if c in df.columns]
st.dataframe(df[colonnes_a_afficher])
