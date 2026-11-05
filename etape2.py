# ÉTAPE 2 — Le widget EST une variable (≈ 2 min)
# Montrer : chaque fois qu'on touche un filtre, le script repart de la ligne 1.
import pandas as pd
import streamlit as st

st.title("🎿 Stations de ski françaises")

df = pd.read_csv("demo/stations.csv")

# --- Barre latérale : les filtres ---
st.sidebar.header("Filtres")
massifs = st.sidebar.multiselect("Massif", sorted(df.massif.unique()), default=sorted(df.massif.unique()))
alt_min = st.sidebar.slider("Altitude max d'au moins (m)", 1000, 3800, 2000, step=100)
budget = st.sidebar.slider("Budget forfait (€ / jour)", 25, 80, 80)

filtre = df[df.massif.isin(massifs) & (df.altitude_max >= alt_min) & (df.forfait_jour <= budget)]

# --- Indicateurs ---
c1, c2, c3 = st.columns(3)
c1.metric("Stations", len(filtre))
c2.metric("Km de pistes", int(filtre.km_pistes.sum()))
c3.metric("Forfait moyen", f"{filtre.forfait_jour.mean():.0f} €" if len(filtre) else "—")

st.dataframe(filtre, hide_index=True)

st.toast(f"Script relancé à {pd.Timestamp.now():%H:%M:%S}")  # preuve visible du rerun
