import streamlit as st
import pandas as pd

url = "https://docs.google.com/spreadsheets/d/1L2tPAY-SjzQCHeT7v9VL_qsgQmV90kz21M1lql9KvN8/export?format=csv"
df = pd.read_csv(url)

colonnes_admin = [
    "Horodatage",
    "Adresse e-mail", 
    "NINEA", 
    "RAISON SOCIALE", 
    "Adresse", 
    "Nature d'impôt", 
    "Centre Fiscal"
]

df_filtre = df[[col for col in colonnes_admin if col in df.columns]]

st.title("Situation Administrative")
st.dataframe(df_filtre)
