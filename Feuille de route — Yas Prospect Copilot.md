# Feuille de route — Yas Prospect Copilot

## Équipe & Rôles

| Membre           | Rôle          | Responsabilités                                 |
| ---------------- | ------------- | ----------------------------------------------- |
| **Dev Python 1** | Lead Front    | Interface Streamlit, onglet Recherche & Scoring |
| **Dev Python 2** | Lead Back     | LLM Groq, Webhook Discord, Pipeline statuts     |
| **Data**         | Data Engineer | Dataset CSV, SQLite, Google Sheets backup       |
| **Scénario**     | Product/Demo  | Script démo, slides scalabilité, coordination   |
| **Chiffres**     | Analyste      | Métriques 4h→15min, critères d'évaluation, QA   |

---

## ÉTAPE 1 — Fondations

**Livrable : scoring fonctionnel en CLI**

- **Dev Python 1** → Setup Git + repo `Telecom-prospect-IA`, structure de fichiers, `requirements.txt`, `README.md`
- **Data** → Saisie du dataset 12 entreprises togolaises dans `data/entreprises.csv` (toutes les colonnes du schéma)
- **Dev Python 1** → Écrire `scoring.py` + tester les 12 cas
- **Dev Python 2** → Écrire `database.py` : table SQLite, import CSV, CRUD (insert, select, update statut)
- **Tous** → Revue collective : vérifier scores attendus (Ecobank = 100, Boulangerie = 15)

✅ **Critère de succès** : `python scoring.py` retourne les bons scores pour les 12 entreprises

---

## ÉTAPE 2 — Interface + LLM

**Livrable : interface fonctionnelle avec scoring + génération**

- **Dev Python 1** → Onglet 1 Streamlit "Recherche & Scoring" : filtres (secteur, localisation, effectif), bouton "Rechercher", tableau des résultats, clic ligne → détail des 4 raisons du score
- **Dev Python 2** → Écrire `llm.py` : appel API Groq avec prompt exact du cahier des charges + fallback 2ème clé API
- **Dev Python 2** → Bouton "Générer message" dans l'interface + affichage temps réel
- **Data** → Mise à jour SQLite avec colonnes `message_genere` et `statut`
- **Tous** → Tests bout-en-bout : sélection → scoring → génération → latence < 2s

✅ **Critère de succès** : email en français généré en < 5 secondes, scoring détaillé affiché

---

## ÉTAPE 3 — Pipeline + Handoff

**Livrable : prototype complet + script démo**

- **Dev Python 1** → Onglet 2 "Pipeline" : vue kanban des statuts, boutons (Générer, Relancer, Convertir), mise à jour statut en base
- **Dev Python 2** → Simulation relance J+3 : si statut = "Contacté", générer message de relance avec ton différent
- **Dev Python 2** → Écrire `webhook.py` : notification Discord avec message de handoff structuré + fallback Streamlit si échec
- **Data** → Google Sheets backup : sync depuis SQLite, lien partagé accessible au jury
- **Scénario + Chiffres** → Rédiger `demo/demo_script.md` mot pour mot (ouverture, 4 étapes, clôture) + slides scalabilité (5 goulots + solutions)
- **Tous** → Parcours complet : Identifier → Qualifier → Prospecter → Relancer → Convertir → notification Discord visible

✅ **Critère de succès** : démo bout-en-bout sans intervention manuelle

---

## ÉTAPE 4 — Répétition + Vidéo

**Livrable : démo live prête + vidéo backup**

- **Tous** → Répétition 1 complète (5 min chrono) → corrections des bugs
- **Tous** → Enregistrement vidéo de secours (OBS ou Loom) en 4K, même scénario que la démo live
- **Tous** → Répétition 2 + ajustements fluidité/timing
- **Scénario + Chiffres** → Finalisation slides scalabilité + préparation réponses aux questions du jury
- **Tous** → Répétition 3 + checklist complète (17 points)
- **Chiffres** → Vérification et justification chiffrée 4h → 15min

✅ **Critère de succès** : checklist complète cochée, vidéo backup testée, script répété 3 fois

---

## Priorités absolues (si le temps manque)

1. **Obligatoire** : `scoring.py` + `database.py` + onglet Recherche
2. **Obligatoire** : `llm.py` + bouton "Générer message"
3. **Obligatoire** : Webhook Discord (effet "wow" de la démo)
4. **Optionnel** : Google Sheets backup, tableau de bord, slides avancées

---

## Points de vigilance critiques

- **Clés API Groq** : une clé par Dev Python 2, fallback configuré dès l'Étape 2
- **Dataset réaliste** : scores variés (pas tous à 100) pour crédibiliser le scoring
- **Webhook Discord** : serveur + webhook créés dès l'Étape 1 pour ne pas bloquer l'Étape 3
- **Vidéo backup** : enregistrée **avant** la dernière répétition
- **Démo en local** : PC avec connexion stable + hotspot de secours

---

## Structure de fichiers

```
Telecom-prospect-IA/
├── app.py
├── scoring.py
├── llm.py
├── database.py
├── webhook.py
├── data/
│   └── entreprises.csv
├── demo/
│   └── demo_script.md
├── requirements.txt
└── README.md
```
