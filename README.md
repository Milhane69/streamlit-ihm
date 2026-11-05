# Exposé IHM · Streamlit (Groupe 5)

Appli de participation en direct pour l'exposé, plus les 4 étapes de la démo.

```
app.py              appli de vote (téléphones + régie présentateur)
requirements.txt
demo/stations.csv   jeu de données de la démo
demo/etape1.py … etape4.py
```

## 1. Tester en local (5 min)

```bash
pip install -r requirements.txt
streamlit run app.py
```

- Vue public : http://localhost:8501
- Régie : http://localhost:8501/?p=admin&key=ihm2026

Ouvrez la vue public dans 2 ou 3 onglets (ou sur votre téléphone, sur le même Wi-Fi, à l'adresse « Network URL » affichée dans le terminal) pour simuler la salle.

## 2. Mettre en ligne (Streamlit Community Cloud, gratuit)

1. Créez un dépôt GitHub public avec le contenu de ce dossier.
2. Allez sur share.streamlit.io → « Create app » → choisissez le dépôt, fichier principal `app.py`.
3. Dans « App URL », choisissez exactement **ihm-streamlit-g5** : le QR code du PowerPoint pointe vers `https://ihm-streamlit-g5.streamlit.app`.
   - Si ce nom est déjà pris, prenez-en un autre, changez `PUBLIC_URL` dans `app.py` et demandez-moi de régénérer les QR codes.
4. Dans « Advanced settings → Secrets », mettez une clé à vous :
   ```
   ADMIN_KEY = "votre-clé-secrète"
   ```
   La régie sera alors sur `https://ihm-streamlit-g5.streamlit.app/?p=admin&key=votre-clé-secrète`.

## 3. Le jour J

- **10 min avant** : ouvrez l'appli, car Community Cloud met en veille les applis inactives et le réveil prend un peu de temps.
- Ouvrez la régie dans un onglet du navigateur, le PowerPoint en plein écran, et passez de l'un à l'autre avec Alt+Tab.
- Les slides rouges « À vous de jouer » = choisir l'activité correspondante dans la régie (barre latérale). Le numéro de l'activité est indiqué dans les notes de chaque slide.
- « Révéler la bonne réponse » (interrupteur de la régie) affiche la bonne réponse pour les questions « Combien de lignes ? » et « Prédiction ».
- Quiz : boutons Précédente / Révéler / Suivante. Après la 7e question, « Suivante » affiche le podium.
- Après le cours : « Tout réinitialiser ».

## 4. La démo

Lancez depuis ce dossier :

```bash
streamlit run demo/etape1.py   # puis etape2, etape3, etape4
```

À l'étape 3, remplacez `CHOIX = "carte"` par le choix de la salle (`"histogramme"`, `"courbe"` ou `"nuage"`) et enregistrez.

## Limites connues

Les votes sont gardés en mémoire du serveur : si l'appli redémarre en plein exposé, ils repartent de zéro (c'est d'ailleurs un bon exemple de limite à mentionner). Plan B : des captures d'écran des résultats et de la démo.
