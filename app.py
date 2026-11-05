"""
Exposé IHM — Streamlit (Groupe 5 : Mahdi DJENNAD & Milhane RABEHI)
Appli de participation en direct : la salle vote sur son téléphone,
les présentateurs pilotent et affichent les résultats au vidéoprojecteur.

  Public       : https://<votre-app>.streamlit.app
  Présentateur : https://<votre-app>.streamlit.app/?p=admin&key=<ADMIN_KEY>

Lancer en local : streamlit run app.py
"""
import threading
import time
import uuid
from collections import Counter

import pandas as pd
import streamlit as st

st.set_page_config(page_title="IHM · Streamlit en direct", page_icon="🎈", layout="centered")

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
try:
    ADMIN_KEY = st.secrets["ADMIN_KEY"]
except Exception:
    ADMIN_KEY = "ihm2026"  # à changer dans les Secrets de Streamlit Community Cloud

PUBLIC_URL = "https://ihm-streamlit-g5.streamlit.app"  # adresse finale de l'appli

ACTIVITIES = {
    "accueil": {"label": "⏳ Salle d'attente", "type": "wait"},
    "mot": {
        "label": "1 · Un mot pour une bonne interface",
        "type": "text",
        "question": "En UN seul mot : qu'est-ce qu'une bonne interface ?",
    },
    "dashboard": {
        "label": "2 · Le défi du vendredi",
        "type": "choice",
        "question": "Un client veut un tableau de bord interactif sur ses données… pour vendredi. Vous partez sur :",
        "options": [
            "React + une API Flask",
            "Excel + des macros",
            "Power BI / Tableau",
            "Un script Python… et une prière",
        ],
    },
    "langage": {
        "label": "3 · Votre langage",
        "type": "choice",
        "question": "Quel langage utilisez-vous le plus ?",
        "options": ["Python", "JavaScript / TypeScript", "Java", "C / C++", "Autre"],
    },
    "lignes": {
        "label": "4 · Combien de lignes ?",
        "type": "choice",
        "question": "Combien de lignes de Python faut-il pour une appli web avec un curseur interactif ?",
        "options": ["3", "30", "300", "3 000"],
        "answer": "3",
    },
    "rerun": {
        "label": "5 · Prédiction : le curseur",
        "type": "choice",
        "question": "Je bouge un curseur dans une appli Streamlit. Que se passe-t-il côté Python ?",
        "options": [
            "Seule la fonction liée au curseur s'exécute",
            "TOUT le script est relancé de haut en bas",
            "Le navigateur calcule tout seul en JavaScript",
            "Rien, il faut cliquer sur « Valider »",
        ],
        "answer": "TOUT le script est relancé de haut en bas",
    },
    "demo": {
        "label": "6 · Vous choisissez la démo",
        "type": "choice",
        "question": "Démo en direct : quelle visualisation ajoutons-nous à l'appli ?",
        "options": ["🗺️ Une carte", "📊 Un histogramme", "📈 Une courbe", "🔵 Un nuage de points"],
    },
    "debat": {
        "label": "7 · Débat",
        "type": "choice",
        "question": "Streamlit pour une appli grand public (des milliers d'utilisateurs, design sur mesure) ?",
        "options": ["👍 Pour", "👎 Contre", "🤔 Ça dépend"],
    },
    "quiz": {"label": "8 · Quiz final", "type": "quiz"},
    "avis": {
        "label": "9 · Votre avis",
        "type": "stars",
        "question": "Notez l'exposé (soyez honnêtes, c'est anonyme 😉)",
    },
}

QUIZ = [
    {
        "q": "Que fait Streamlit quand un widget change de valeur ?",
        "o": ["Il relance tout le script", "Il recharge la page entière", "Il appelle un callback JavaScript", "Il redémarre le serveur"],
        "a": 0,
    },
    {
        "q": "Quel décorateur évite de recharger un gros CSV à chaque interaction ?",
        "o": ["@st.cache_data", "@st.memo", "@st.static", "@lru_cache_web"],
        "a": 0,
    },
    {
        "q": "Où garder une valeur (ex. un compteur) entre deux exécutions du script ?",
        "o": ["Une variable globale", "st.session_state", "Un cookie", "st.sidebar"],
        "a": 1,
    },
    {
        "q": "Quelle entreprise a racheté Streamlit en 2022 ?",
        "o": ["Microsoft", "Google", "Snowflake", "Databricks"],
        "a": 2,
    },
    {
        "q": "Quelle commande lance une appli Streamlit ?",
        "o": ["python app.py --web", "streamlit start", "streamlit run app.py", "npm run streamlit"],
        "a": 2,
    },
    {
        "q": "Quel concurrent est surtout pensé pour les démos de modèles d'IA (Hugging Face) ?",
        "o": ["Dash", "Gradio", "Shiny", "Angular"],
        "a": 1,
    },
    {
        "q": "Principale limite IHM de Streamlit ?",
        "o": ["Pas de graphiques", "Mise en page et design peu personnalisables", "Impossible à déployer", "Payant"],
        "a": 1,
    },
]
QUIZ_LETTERS = ["🟥", "🟦", "🟨", "🟩"]


# --------------------------------------------------------------------------
# État partagé entre TOUS les utilisateurs (un seul objet en mémoire serveur)
# C'est exactement ce que fait st.cache_resource : une ressource globale.
# --------------------------------------------------------------------------
@st.cache_resource
def get_store():
    return {
        "lock": threading.Lock(),
        "active": "accueil",
        "votes": {},        # activité -> {voter_id: réponse}
        "players": {},      # voter_id -> pseudo
        "quiz_idx": 0,
        "quiz_open_at": time.time(),
        "quiz_reveal": False,
        "quiz_answers": {},  # idx -> {voter_id: (option, secondes)}
        "scores": {},       # voter_id -> points
    }


store = get_store()


def vote(activity, voter, value):
    with store["lock"]:
        store["votes"].setdefault(activity, {})[voter] = value


def results(activity):
    with store["lock"]:
        return dict(store["votes"].get(activity, {}))


def set_active(key):
    with store["lock"]:
        store["active"] = key


# --------------------------------------------------------------------------
# Identité anonyme du téléphone (session_state survit aux reruns)
# --------------------------------------------------------------------------
if "voter_id" not in st.session_state:
    st.session_state.voter_id = uuid.uuid4().hex[:10]
VOTER = st.session_state.voter_id

st.markdown(
    """
    <style>
      .big-q {font-size: 1.35rem; font-weight: 700; line-height: 1.35; margin: .4rem 0 1rem;}
      .huge {font-size: 2.6rem; font-weight: 800; line-height: 1.15;}
      .muted {opacity: .65;}
      div.stButton > button {width: 100%; min-height: 3.2rem; font-size: 1.05rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def bar(counter: Counter, options=None, highlight=None):
    labels = options if options else [k for k, _ in counter.most_common(12)]
    df = pd.DataFrame({"Réponse": labels, "Votes": [counter.get(l, 0) for l in labels]})
    st.bar_chart(df, x="Réponse", y="Votes", horizontal=True, color="#FF4B4B", height=60 + 45 * len(labels))
    if highlight:
        st.success(f"✅ Bonne réponse : **{highlight}**")


# ==========================================================================
# VUE PRÉSENTATEUR  (?p=admin&key=...)
# ==========================================================================
def presenter_view():
    st.sidebar.title("🎛️ Régie")
    keys = list(ACTIVITIES)
    current = store["active"]
    choice = st.sidebar.radio(
        "Activité en direct sur les téléphones",
        keys,
        index=keys.index(current),
        format_func=lambda k: ACTIVITIES[k]["label"],
    )
    if choice != current:
        set_active(choice)
        if choice == "quiz":
            with store["lock"]:
                store["quiz_open_at"] = time.time()
        st.rerun()

    st.sidebar.divider()
    show_answer = st.sidebar.toggle("Révéler la bonne réponse", value=False)
    if st.sidebar.button("🧹 Effacer les votes de cette activité"):
        with store["lock"]:
            store["votes"].pop(choice, None)
    if st.sidebar.button("♻️ Tout réinitialiser", type="secondary"):
        with store["lock"]:
            store.update(votes={}, players={}, quiz_idx=0, quiz_reveal=False,
                         quiz_answers={}, scores={}, quiz_open_at=time.time())
        st.rerun()
    try:
        import qrcode
        img = qrcode.make(PUBLIC_URL)
        st.sidebar.image(img.get_image(), caption=PUBLIC_URL)
    except Exception:
        st.sidebar.caption(PUBLIC_URL)

    act = ACTIVITIES[choice]
    if act["type"] == "quiz":
        presenter_quiz()
    else:
        presenter_results(choice, act, show_answer)


@st.fragment(run_every=1.5)
def presenter_results(key, act, show_answer):
    res = results(key)
    st.caption(f"👥 {len(res)} réponse(s) · mise à jour automatique")
    if act["type"] == "wait":
        st.markdown('<div class="huge">Scannez le QR code 📱</div>', unsafe_allow_html=True)
        st.markdown(f"### {PUBLIC_URL.replace('https://', '')}")
        st.metric("Téléphones connectés", len(store["players"]) or "—")
        return
    st.markdown(f'<div class="big-q">{act["question"]}</div>', unsafe_allow_html=True)
    if act["type"] == "text":
        words = Counter(v.strip().lower() for v in res.values() if v.strip())
        if words:
            top = words.most_common(1)[0][0]
            st.markdown(f'<div class="huge">« {top} »</div>', unsafe_allow_html=True)
            bar(words)
    elif act["type"] == "choice":
        bar(Counter(res.values()), act["options"], act.get("answer") if show_answer else None)
    elif act["type"] == "stars":
        if res:
            notes = [v + 1 for v in res.values()]
            st.metric("Note moyenne", f"{sum(notes) / len(notes):.1f} / 5 ⭐")
            bar(Counter(f"{n} ⭐" for n in notes), [f"{n} ⭐" for n in range(1, 6)])


def presenter_quiz():
    c1, c2, c3 = st.columns(3)
    idx = store["quiz_idx"]
    if c1.button("⬅️ Précédente", disabled=idx == 0):
        with store["lock"]:
            store["quiz_idx"] -= 1
            store["quiz_reveal"] = False
            store["quiz_open_at"] = time.time()
        st.rerun()
    if c2.button("👀 Révéler"):
        with store["lock"]:
            store["quiz_reveal"] = True
        st.rerun()
    if c3.button("Suivante ➡️", disabled=idx >= len(QUIZ)):
        with store["lock"]:
            store["quiz_idx"] += 1
            store["quiz_reveal"] = False
            store["quiz_open_at"] = time.time()
        st.rerun()
    presenter_quiz_live()


@st.fragment(run_every=1.0)
def presenter_quiz_live():
    idx = store["quiz_idx"]
    if idx >= len(QUIZ):
        st.markdown('<div class="huge">🏆 Podium</div>', unsafe_allow_html=True)
        leaderboard(10)
        return
    q = QUIZ[idx]
    answers = store["quiz_answers"].get(idx, {})
    elapsed = int(time.time() - store["quiz_open_at"])
    st.caption(f"Question {idx + 1}/{len(QUIZ)} · ⏱️ {elapsed}s · 👥 {len(answers)} réponse(s)")
    st.markdown(f'<div class="big-q">{q["q"]}</div>', unsafe_allow_html=True)
    for i, o in enumerate(q["o"]):
        good = store["quiz_reveal"] and i == q["a"]
        st.markdown(f"#### {QUIZ_LETTERS[i]} {o} {'✅' if good else ''}")
    if store["quiz_reveal"]:
        counts = Counter(q["o"][opt] for opt, _ in answers.values())
        bar(counts, q["o"])
        leaderboard(5)


def leaderboard(n):
    with store["lock"]:
        scores = dict(store["scores"])
        names = dict(store["players"])
    if not scores:
        st.info("Pas encore de points.")
        return
    top = sorted(scores.items(), key=lambda kv: -kv[1])[:n]
    medals = ["🥇", "🥈", "🥉"] + ["  "] * 20
    for rank, (vid, pts) in enumerate(top):
        st.markdown(f"### {medals[rank]} {names.get(vid, 'Anonyme')} — {pts} pts")


# ==========================================================================
# VUE PUBLIC (téléphones)
# ==========================================================================
def audience_view():
    st.title("🎈 Exposé IHM · Streamlit")
    if VOTER not in store["players"]:
        with st.form("pseudo"):
            name = st.text_input("Ton pseudo (pour le classement du quiz)", max_chars=20)
            if st.form_submit_button("Je rejoins la salle 🚀"):
                with store["lock"]:
                    store["players"][VOTER] = name.strip() or f"Anonyme-{VOTER[:3]}"
                st.rerun()
        st.caption("Aucune donnée personnelle conservée. Tout est effacé à la fin du cours.")
        return
    st.caption(f"Connecté·e en tant que **{store['players'][VOTER]}**")
    audience_live()


@st.fragment(run_every=2)
def audience_live():
    key = store["active"]
    act = ACTIVITIES[key]
    if act["type"] == "wait":
        st.markdown('<div class="big-q">Bienvenue ! 👋</div>', unsafe_allow_html=True)
        st.write("Garde cette page ouverte : les questions apparaîtront ici toutes seules, au fil de l'exposé.")
        st.caption("Petit spoiler : cette page est elle-même une appli Streamlit 😉")
        return
    if act["type"] == "quiz":
        audience_quiz()
        return

    already = VOTER in results(key)
    st.markdown(f'<div class="big-q">{act["question"]}</div>', unsafe_allow_html=True)
    if already:
        st.success("Réponse enregistrée ✅ Regarde l'écran !")
        return
    if act["type"] == "text":
        with st.form(f"f_{key}", clear_on_submit=True):
            word = st.text_input("Ton mot", max_chars=25)
            if st.form_submit_button("Envoyer"):
                if word.strip():
                    vote(key, VOTER, word.strip().split()[0])
                    st.rerun(scope="fragment")
    elif act["type"] == "choice":
        for opt in act["options"]:
            if st.button(opt, key=f"{key}_{opt}"):
                vote(key, VOTER, opt)
                st.rerun(scope="fragment")
    elif act["type"] == "stars":
        note = st.feedback("stars", key=f"stars_{key}")
        if note is not None:
            vote(key, VOTER, note)
            st.rerun(scope="fragment")


def audience_quiz():
    idx = store["quiz_idx"]
    if idx >= len(QUIZ):
        st.markdown('<div class="big-q">Quiz terminé ! 🏁</div>', unsafe_allow_html=True)
        st.metric("Ton score", f"{store['scores'].get(VOTER, 0)} pts")
        return
    q = QUIZ[idx]
    answers = store["quiz_answers"].get(idx, {})
    st.caption(f"Question {idx + 1}/{len(QUIZ)}")
    st.markdown(f'<div class="big-q">{q["q"]}</div>', unsafe_allow_html=True)
    if VOTER in answers:
        opt, secs = answers[VOTER]
        if store["quiz_reveal"]:
            if opt == q["a"]:
                st.success("Bravo, bonne réponse ! 🎉")
                flag = f"balloons_{idx}"
                if not st.session_state.get(flag):  # une seule fois, pas à chaque rafraîchissement
                    st.session_state[flag] = True
                    st.balloons()
            else:
                st.error(f"Raté… c'était : {q['o'][q['a']]}")
        else:
            st.info(f"Réponse envoyée en {secs:.1f}s ⏱️ Suspense…")
        st.metric("Ton score", f"{store['scores'].get(VOTER, 0)} pts")
        return
    if store["quiz_reveal"]:
        st.warning("Trop tard pour cette question ⏰")
        return
    for i, o in enumerate(q["o"]):
        if st.button(f"{QUIZ_LETTERS[i]}  {o}", key=f"quiz_{idx}_{i}"):
            secs = time.time() - store["quiz_open_at"]
            with store["lock"]:
                store["quiz_answers"].setdefault(idx, {})[VOTER] = (i, secs)
                if i == q["a"]:
                    # 1000 pts max : 500 pour la bonne réponse + bonus de rapidité
                    store["scores"][VOTER] = store["scores"].get(VOTER, 0) + 500 + max(0, int(500 - 25 * secs))
            st.rerun(scope="fragment")


# ==========================================================================
# Routage par paramètre d'URL
# ==========================================================================
params = st.query_params
if params.get("p") == "admin":
    if params.get("key") == ADMIN_KEY:
        presenter_view()
    else:
        st.error("Clé présentateur invalide.")
else:
    audience_view()
