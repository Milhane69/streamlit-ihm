# ÉTAPE 3 — La salle a choisi la visualisation (≈ 3 min)
# En live : changer la valeur de CHOIX selon le vote, sauvegarder -> l'appli se met à jour.
import pandas as pd
import streamlit as st

CHOIX = "carte"  # "carte" | "histogramme" | "courbe" | "nuage"

st.title("🎿 Stations de ski françaises")
df = pd.read_csv("demo/stations.csv")

st.sidebar.header("Filtres")
massifs = st.sidebar.multiselect("Massif", sorted(df.massif.unique()), default=sorted(df.massif.unique()))
budget = st.sidebar.slider("Budget forfait (€ / jour)", 25, 80, 80)
filtre = df[df.massif.isin(massifs) & (df.forfait_jour <= budget)]

c1, c2, c3 = st.columns(3)
c1.metric("Stations", len(filtre))
c2.metric("Km de pistes", int(filtre.km_pistes.sum()))
c3.metric("Forfait moyen", f"{filtre.forfait_jour.mean():.0f} €" if len(filtre) else "—")

if CHOIX == "carte":
    st.subheader("🗺️ Où sont les stations ?")
    st.map(filtre, latitude="lat", longitude="lon", size=4000, color="#FF4B4B")
elif CHOIX == "histogramme":
    st.subheader("📊 Km de pistes par station")
    st.bar_chart(filtre, x="station", y="km_pistes", color="#FF4B4B")
elif CHOIX == "courbe":
    st.subheader("📈 Prix du forfait selon l'altitude")
    st.line_chart(filtre.sort_values("altitude_max"), x="altitude_max", y="forfait_jour", color="#FF4B4B")
else:
    st.subheader("🔵 Taille du domaine vs prix")
    st.scatter_chart(filtre, x="km_pistes", y="forfait_jour", color="massif", size="altitude_max")

with st.expander("Voir les données"):
    st.dataframe(filtre, hide_index=True)
