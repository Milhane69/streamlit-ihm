# ÉTAPE 1 — Un script Python devient une page web (≈ 1 min)
# Lancer : streamlit run demo/etape1.py
import pandas as pd
import streamlit as st

st.title("🎿 Stations de ski françaises")
st.write("Mon premier tableau de bord, en quelques lignes de Python.")

df = pd.read_csv("demo/stations.csv")
st.dataframe(df)  # tableau triable, filtrable, redimensionnable… sans une ligne de JS

st.caption("Données approximatives, à but pédagogique.")
