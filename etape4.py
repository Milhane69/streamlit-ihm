# ÉTAPE 4 — Les 2 réflexes indispensables : cache et état (≈ 3 min)
# 1) Commenter/décommenter @st.cache_data : sans lui, chaque clic attend 2 secondes.
# 2) Le compteur de favoris ne survit aux reruns QUE grâce à st.session_state.
import time

import pandas as pd
import streamlit as st

st.title("🎿 Stations de ski françaises")


@st.cache_data  # <- à commenter en live pour montrer la lenteur
def charger():
    time.sleep(2)  # on simule une grosse base de données lente
    return pd.read_csv("demo/stations.csv")


df = charger()

budget = st.slider("Budget forfait (€ / jour)", 25, 80, 80)
filtre = df[df.forfait_jour <= budget]

# --- Favoris : l'état qui survit aux reruns ---
if "favoris" not in st.session_state:
    st.session_state.favoris = []

choix = st.selectbox("Ajouter une station à mes favoris", filtre.station)
if st.button("⭐ Ajouter"):
    if choix not in st.session_state.favoris:
        st.session_state.favoris.append(choix)

st.write("**Mes favoris :**", ", ".join(st.session_state.favoris) or "aucun pour l'instant")

# --- Bonus : un assistant façon chat (st.chat_input) ---
question = st.chat_input("Pose une question : ex. « moins chère »")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        if "chère" in question.lower() or "cher" in question.lower():
            s = filtre.nsmallest(1, "forfait_jour").iloc[0]
            st.write(f"La moins chère dans ton budget : **{s.station}** à {s.forfait_jour} €.")
        elif "haut" in question.lower():
            s = filtre.nlargest(1, "altitude_max").iloc[0]
            st.write(f"La plus haute : **{s.station}** ({s.altitude_max} m).")
        else:
            st.write("Essaie « moins chère » ou « plus haute » 😉")
