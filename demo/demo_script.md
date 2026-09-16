# Script de démo — Yas Prospect Copilot
**Durée totale : 5 minutes** | **Répéter 3 fois minimum avant la présentation**

---

## ⚙️ Checklist pré-démo (à faire 10 min avant)

- [ ] `streamlit run app.py` lancé et page ouverte dans Chrome
- [ ] Serveur Discord ouvert sur un second écran (ou onglet)
- [ ] Connexion internet stable (ou hotspot de secours prêt)
- [ ] Fenêtre Streamlit en plein écran, zoom navigateur à 90%
- [ ] Prospect **"Togo Logistique SA"** visible dans le pipeline (statut : Relancé)
- [ ] Prospect **"Ecobank Togo"** visible (statut : Converti)
- [ ] 2 clés API Groq dans `.env` (ou messages simulés prêts en fallback)

---

## 🎬 OUVERTURE — 30 secondes

> **[Regarder le jury, sourire, lancer sans hésiter]**

**Dire :**
> « Un commercial Yas Business perd aujourd'hui **4 heures par jour** à chercher manuellement des prospects, qualifier leur potentiel, rédiger des emails, suivre les relances.
> En 4 jours, zéro budget, avec une équipe de 5 personnes — voici notre réponse : **Yas Prospect Copilot**. »

**Montrer :** le bandeau des 4 métriques en haut de l'interface
> « 12 prospects traités, 8 haute priorité, 1 déjà converti, taux de conversion 8 %. »

---

## 🔍 ÉTAPE 1 — Identifier (1 minute)

**Dire :**
> « Premier problème des commerciaux : trouver les bonnes entreprises. On clique sur l'onglet **Recherche & Scoring**. »

**Action :** Cliquer sur l'onglet **🔍 Recherche & Scoring**

**Dire :**
> « Je cherche des entreprises dans la **Logistique**, à **Lomé**, entre **10 et 49 salariés**. »

**Action :** Sélectionner dans les filtres :
- Secteur → **Logistique**
- Localisation → **Lomé**
- Effectif → **10–49**

**Action :** Cliquer sur **🔍 Rechercher**

**Dire :**
> « Résultat immédiat. Le système a trouvé **Togo Logistique SA** avec un score de **90 sur 100**. »

---

## 📊 ÉTAPE 2 — Qualifier (1 minute 30)

**Dire :**
> « Mais ce n'est pas juste un score — chaque décision de l'IA est **expliquée par une raison métier**. Je clique sur la ligne. »

**Action :** Cliquer sur la ligne **Togo Logistique SA** dans le tableau

**Dire en lisant les 4 raisons à voix haute :**
> - « **+25** — Secteur prioritaire : Logistique »
> - « **+20** — Taille correcte : 45 salariés »
> - « **+20** — Lomé, couverture Fibre optimale »
> - « **+25** — Signal d'expansion : recrutement de profils informatique pour la traçabilité »

**Dire :**
> « Score total : **90 sur 100**. Ce prospect est qualifié haute priorité. »

**[Si la comparaison est visible, la montrer :]**
> « En face, la **Boulangerie de la Paix** : 15 sur 100. Hors zone, hors taille, aucun signal. Le scoring **discrimine réellement**. »

---

## ✉️ ÉTAPE 3 — Prospecter (1 minute)

**Dire :**
> « Maintenant, on passe dans le **Pipeline**. Je clique sur Gérer pour Togo Logistique SA. »

**Action :** Cliquer sur l'onglet **📋 Pipeline**

**Action :** Trouver **Togo Logistique SA** (colonne Relancé) → cliquer **Gérer →**

**Dire :**
> « En un clic, je génère un email de prospection personnalisé, rédigé par l'IA Groq en moins de 2 secondes. »

**Action :** Cliquer sur **✉️ Générer message de contact**

**[Pendant le spinner — environ 1-2 secondes :]**
> « Le modèle, c'est Llama 3.3 70 milliards de paramètres, hébergé par Groq. »

**[Lire le message généré à voix haute — insister sur la personnalisation :]**
> « Vous voyez — il cite directement *le recrutement informatique pour la traçabilité*. Ce n'est pas un template générique, c'est un message **ancré dans la réalité de cette entreprise**. »

---

## 🔁 ÉTAPE 4 — Relancer & Convertir (1 minute)

**Dire :**
> « Trois jours passent, pas de réponse. Le système génère automatiquement une **relance J+3**, avec un ton plus direct. »

**Action :** *(si statut = Contacté)* Cliquer sur **🔁 Générer relance J+3**
*(sinon, montrer le message déjà en statut Relancé et expliquer le mécanisme)*

**Dire :**
> « Aujourd'hui, Togo Logistique SA a répondu positivement. Je clique **Converti**. »

**Action :** *(sur un prospect en statut Contacté ou Relancé)* Cliquer **✅ Marquer comme Converti**

**Dire :**
> « Et maintenant — la partie visible pour le jury — je vais dans l'onglet **Handoff** et je transmets au responsable commercial. »

**Action :** Cliquer sur l'onglet **🤝 Handoff**

**Action :** Trouver le prospect converti → cliquer **📤 Transmettre à Discord**

**[Pointer l'écran Discord / l'onglet Discord en direct :]**
> « La notification arrive **en temps réel** sur Discord — nom, secteur, score, message envoyé. Le responsable commercial est informé immédiatement. »

---

## 🏁 CLÔTURE — 30 secondes

**[Revenir sur le bandeau des métriques :]**

**Dire :**
> « Bilan : **12 prospects traités**. Avant ce projet : **4 heures par jour**. Avec Yas Prospect Copilot : **15 minutes**. Gain : **94%**. »

> « Chaque décision est explicable, chaque action est traçable, et l'architecture est conçue pour passer à **1 000 prospects** sans changer une ligne de code applicatif. »

> « Merci. »

**[Garder le silence 2 secondes — laisser l'impact s'installer.]**

---

## ❓ Questions anticipées du jury

| Question probable | Réponse préparée |
|---|---|
| « Pourquoi SQLite et pas une vraie BDD ? » | « SQLite suffit pour 10 000 prospects. La migration vers PostgreSQL est 1 ligne de code — on change juste la chaîne de connexion. » |
| « L'IA peut se tromper dans le scoring ? » | « C'est pourquoi chaque point est explicable. Le commercial voit les raisons et peut corriger. L'IA aide, elle ne décide pas. » |
| « Comment vous passez à 1 000 entreprises ? » | « 5 goulots identifiés, 5 solutions concrètes. SQLite → PostgreSQL, Groq → templates pour scores < 75, Streamlit → FastAPI + React. » |
| « Et la vraie donnée, elle vient d'où ? » | « Aujourd'hui CFE Togo simulé. Demain : scraping légal LinkedIn, import Excel des commerciaux, ou API CFE officielle. » |
| « Pourquoi Discord pour le handoff ? » | « C'est l'outil de communication de l'équipe. En production : même logique avec Slack, email ou CRM via webhook. » |

---

## ⚠️ Plan B — Si Streamlit plante pendant la démo

1. **Ouvrir immédiatement le Google Sheet backup** (lien dans le README)
2. Continuer la démo en expliquant les données depuis le Sheet
3. **Lancer la vidéo de secours** si le Sheet ne suffit pas

> *La vidéo de secours doit être testée et prête sur le bureau de l'ordinateur de démo.*

---

## ⏱️ Timing de répétition

| Répétition | Objectif | Durée |
|---|---|---|
| **Répétition 1** (Jour 4 matin) | Fluidité du parcours, aucun bogue | 5 min + 10 min corrections |
| **Répétition 2** (Jour 4 après-midi) | Timing précis, voix assurée | 5 min chrono |
| **Répétition 3** (Jour 4 fin) | Conditions réelles, réponses jury | 5 min + 5 min Q&A simulé |
