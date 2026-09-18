# Guide de démonstration — CibleNet

> **Version** : 1.0 · **Public** : Commercial, formateur, jury  
> **Durée estimée** : 10 à 15 minutes pour une démo complète

---

## Présentation rapide

**CibleNet** est un assistant commercial IA développé pour **Opticom Business (Togo)**.  
Il automatise les 4 étapes de la prospection B2B :

```
Identifier → Qualifier (Score ICP) → Contacter (message IA) → Convertir (handoff Discord)
```

**Stack technique**
- Interface : Streamlit (Python)
- Base de données : SQLite locale (`data/prospects.db`)
- LLM : Groq API — modèle `qwen/qwen3-8b` (fallback sur données simulées)
- Notification : Webhook Discord
- Scoring : moteur Python pur (4 critères, 0-100 pts)

**Données de démo** : 12 entreprises togolaises fictives, 7 à haute priorité, couvrant les secteurs Banque, Assurance, Logistique, Informatique, Éducation, Commerce et Agroalimentaire.

---

## 1. Lancer l'application

### Prérequis

- Python 3.12 installé
- Environnement virtuel `PS_env` créé

### Commandes de démarrage

```powershell
# 1. Aller dans le dossier du projet
cd "e:\Formation_IA\Lomé_Summer\Projet\Prospect_IA"

# 2. Activer l'environnement virtuel
.\PS_env\Scripts\Activate.ps1

# 3. Lancer l'application
streamlit run app.py
```

L'interface s'ouvre automatiquement dans le navigateur à l'adresse :  
**http://localhost:8501**

### Ce qui se passe au démarrage

- La base SQLite est initialisée si elle n'existe pas
- Les 12 entreprises du CSV sont importées automatiquement
- Les métriques globales s'affichent dans le bandeau supérieur

---

## 2. Vue d'ensemble de l'interface

L'application est structurée en **3 onglets** :

| Onglet | Rôle |
|---|---|
| **Recherche & Scoring** | Filtrer les prospects, voir les scores ICP |
| **Pipeline commercial** | Vue Kanban, générer les messages, gérer les statuts |
| **Handoff Discord** | Transmettre les prospects convertis au responsable commercial |

Le **bandeau de métriques** en haut affiche en temps réel :
- Nombre total de prospects
- Nombre en haute priorité (score ≥ 75)
- Nombre convertis
- Taux de conversion

---

## 3. Onglet 1 — Recherche & Scoring

### Objectif
Montrer comment l'IA identifie et qualifie automatiquement les meilleurs prospects selon le profil client idéal (ICP) d'Opticom Business.

### Étapes de démonstration

**Étape 1 — Recherche sans filtre**
1. Cliquez sur **Rechercher** sans modifier les filtres
2. Les 12 entreprises s'affichent, **triées par score décroissant**
3. Observez : Ecobank Togo et Assurance Sunu en tête avec 100/100

**Étape 2 — Filtrer par secteur**
1. Dans *Secteur d'activité*, sélectionnez **Banque**
2. Cliquez **Rechercher**
3. Seule Ecobank Togo apparaît — score 100/100, haute priorité

**Étape 3 — Voir le détail d'un score**
1. Cliquez sur la ligne **Ecobank Togo** dans le tableau
2. La fiche prospect s'ouvre en dessous avec :
   - Le **badge de score** (vert = haute priorité)
   - Les **4 raisons du score ICP** détaillées
   - La **barre de progression** visuelle
   - Les **tags d'information** : secteur, effectif, ville, site web, paiement en ligne

**Points clés à expliquer**

Le score ICP est calculé sur **4 critères** :

| Critère | Points max | Exemple haute priorité |
|---|---|---|
| Secteur d'activité | 30 pts | Banque / Assurance = 30 pts |
| Taille (effectif) | 25 pts | 50–250 salariés = 25 pts |
| Localisation | 20 pts | Lomé = 20 pts (Fibre optimale) |
| Signal de croissance | 25 pts | Expansion détectée = 25 pts |

**Exemple de comparaison à montrer**
- Cliquez sur **Ecobank Togo** (score 100) → montrez les 4 critères positifs
- Puis montrez en bas la comparaison avec **Boulangerie de la Paix** (score 15)
- Expliquez pourquoi : secteur hors cible + taille inadaptée + hors zone + aucun signal

**Exemple de filtres utiles en démo**

| Filtre | Résultat attendu |
|---|---|
| Secteur : Informatique | 3 entreprises (KBE Digital, Togo Telecom, Startup Fintech) |
| Ville : Kara | 2 entreprises (Clinique de la Paix, Cabinet Conseil) |
| Effectif : ETI 50–250 | 4 entreprises (les mieux dimensionnées) |

---

## 4. Onglet 2 — Pipeline commercial

### Objectif
Montrer le suivi des prospects en temps réel et la génération automatique de messages personnalisés par l'IA.

### Vue Kanban

Les prospects sont répartis en **4 colonnes actives** :

| Colonne | Couleur | Signification |
|---|---|---|
| **Nouveau** | Vert sauge | Prospect identifié, pas encore traité |
| **Scoré** | Or | Score calculé, prêt à être contacté |
| **Contacté** | Bleu | Message de premier contact envoyé |
| **Relancé** | Terre cuite | Relance J+3 générée |

Les prospects clôturés (Converti / Non intéressé / À relancer plus tard) sont dans la section dépliable en bas.

### Étapes de démonstration

**Étape 1 — Sélectionner un prospect**
1. Repérez **Assurance Sunu** dans la colonne *Nouveau* (score 100/100)
2. Cliquez sur **Gérer**
3. Le panneau d'actions s'ouvre en bas de page

**Étape 2 — Générer un message de contact**
1. Cliquez sur **Générer un message de contact**
2. L'IA (Groq / Qwen) rédige un email **personnalisé en moins de 3 secondes** :
   - Mentionne le secteur (Assurance)
   - Cite le signal de croissance (extension régionale)
   - Présente les offres Opticom Business (Fibre Pro, Flotte mobile, API SMS)
   - Propose un rendez-vous de 20 minutes
3. Le statut passe automatiquement à **Contacté**
4. La date du contact est enregistrée

> **Si Groq n'est pas disponible** : le message est tiré des données simulées (CSV). Le résultat est identique visuellement.

**Étape 3 — Générer une relance J+3**
1. Avec le prospect en statut *Contacté*, le bouton **Générer la relance J+3** apparaît
2. Cliquez dessus
3. L'IA rédige un message de relance plus court et plus direct
4. Le statut passe à **Relancé**

**Étape 4 — Convertir un prospect**
1. Cliquez sur **Marquer comme converti**
2. Le prospect disparaît du Kanban actif
3. Il est disponible dans l'onglet **Handoff Discord**

**Autres actions disponibles**

| Bouton | Effet |
|---|---|
| **Non intéressé** | Clôture le prospect, l'archive dans les prospects fermés |
| **À relancer plus tard** | Met en nurture, visible dans les prospects clôturés |

---

## 5. Onglet 3 — Handoff Discord

### Objectif
Montrer la transmission automatique du dossier complet au responsable commercial via Discord.

### Étapes de démonstration

**Étape 1 — Voir les prospects convertis**
1. Les prospects marqués **Converti** apparaissent ici avec leur fiche complète :
   - Nom, secteur, effectif, ville
   - Badge de score ICP
   - Raisons du score (dépliable)
   - Message envoyé (dépliable)

**Étape 2 — Transmettre via Discord**
1. Cliquez sur **Transmettre à Discord**
2. Un message enrichi (embed) est envoyé dans le salon Discord d'Opticom Business avec :
   - Nom du prospect converti
   - Données clés (secteur, effectif, ville, score)
   - Le message de contact envoyé
   - Signature « Opticom Business · CibleNet »

> **Si le webhook Discord n'est pas configuré** : la transmission est simulée sans erreur — parfait pour une démo hors ligne.

### Impact mesuré

La section en bas de l'onglet affiche les gains mesurés :

| Indicateur | Avant (manuel) | Après (Copilot) |
|---|---|---|
| Temps traitement | 4 h / jour | 15 min / jour |
| Gain de productivité | — | **94 %** |

> Mesure basée sur 12 prospects : recherche + qualification + message + handoff en 15 minutes.

---

## 6. Scénario de démo complet (10 min)

Enchaînez ces actions dans l'ordre pour une démonstration fluide :

```
① Onglet Recherche
   → Rechercher sans filtre (12 résultats)
   → Cliquer sur Ecobank Togo → montrer score 100/100 et les 4 raisons
   → Montrer la comparaison avec Boulangerie de la Paix (15/100)

② Onglet Recherche
   → Filtrer Secteur = Informatique → 3 résultats
   → Cliquer sur KBE Digital → montrer le signal de croissance (levée de fonds)

③ Onglet Pipeline
   → Montrer le Kanban (répartition des statuts)
   → Cliquer Gérer sur Assurance Sunu (score 100, statut Nouveau)
   → Générer un message de contact → montrer le texte IA personnalisé
   → Statut passe à "Contacté" automatiquement

④ Onglet Pipeline
   → Cliquer Gérer sur Togo Logistique SA (statut Relancé)
   → Montrer le message de relance J+3 déjà généré

⑤ Onglet Pipeline
   → Cliquer Gérer sur Ecobank Togo (statut Converti existant)
   → Montrer les informations complètes

⑥ Onglet Handoff
   → Voir Ecobank Togo dans la liste des convertis
   → Cliquer Transmettre à Discord
   → Montrer la notification envoyée dans Discord (ou le message simulé)
   → Pointer sur la section Impact mesuré (4h → 15min, 94%)
```

---

## 7. Configuration avant démonstration

### Fichier `.env` (à la racine du projet)

```env
# Clé API Groq (génération de messages par IA)
# Obtenir gratuitement sur https://console.groq.com
GROQ_API_KEY_1=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY_2=gsk_yyyyyyyyyyyyyyyyyyyyyyyyyyyy   # clé de secours (optionnel)

# Webhook Discord (transmission handoff)
# Créer via : Salon Discord → Paramètres → Intégrations → Webhooks
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXXXXXX/YYYYYYY
```

> Sans ces clés, l'application fonctionne en **mode simulation** :
> - Les messages sont tirés des CSV de démo
> - Le handoff Discord est simulé sans erreur
> — idéal pour une démo hors ligne ou sans connexion API.

### Réinitialiser les données pour une démo propre

```powershell
# Supprimer la base SQLite (elle sera recréée au prochain lancement)
Remove-Item "data\prospects.db"

# Relancer l'app — les 12 entreprises sont réimportées depuis le CSV
streamlit run app.py
```

---

## 8. Questions fréquentes en démo

**"Les données sont-elles réelles ?"**  
Non, ce sont des données fictives de démonstration représentatives du tissu économique togolais. En production, le CSV serait alimenté par le CRM ou une extraction LinkedIn/annuaire.

**"Le score est calculé comment ?"**  
Par un moteur Python en 4 critères : secteur (30 pts), effectif (25 pts), localisation (20 pts), signal de croissance (25 pts). Total sur 100. Aucune dépendance externe, modifiable en 5 minutes.

**"Que se passe-t-il si Groq est indisponible ?"**  
Le système bascule automatiquement sur la clé de secours (GROQ_API_KEY_2), puis sur les messages simulés du CSV. L'application ne tombe jamais en erreur.

**"Peut-on ajouter de nouveaux prospects ?"**  
Oui : ajouter des lignes dans `data/entreprises.csv` puis supprimer `data/prospects.db` et relancer l'app. Le score est calculé automatiquement.

**"Le message IA est-il envoyé directement ?"**  
Non — il est généré et affiché pour validation commerciale. C'est le commercial qui décide de l'envoyer. Le Copilot rédige, l'humain valide.

---

## 9. Architecture résumée

```
app.py           ← Interface Streamlit (3 onglets)
├── database.py  ← SQLite : CRUD, pipeline, stats
├── scoring.py   ← Moteur ICP : 4 critères, score 0-100
├── llm.py       ← Groq API : génération messages + fallback
├── webhook.py   ← Discord : envoi handoff
└── data/
    ├── entreprises.csv          ← 12 prospects de démo
    ├── messages_simules.csv     ← Messages fallback (5 emails)
    ├── relances_j3_simulees.csv ← Relances fallback (2 messages)
    └── prospects.db             ← Base SQLite (générée au 1er lancement)
```

---

*Guide rédigé pour Opticom Business · Formation IA · Lomé, Togo*
