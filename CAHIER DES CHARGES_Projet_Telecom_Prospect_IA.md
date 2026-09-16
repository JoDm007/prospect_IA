# CAHIER DES CHARGES FINAL — Projet "Yas Prospect Copilot"

**Version fusionnée : Streamlit (base) + Google Sheets + Webhook Discord + Vidéo secours**

---

**Projet** : Identifier, qualifier et convertir automatiquement les meilleurs prospects B2B pour Yas Togo / Mixx by Yas

**Équipe** : 5 personnes

**Durée** : 4 jours

**Budget** : 0 FCFA

**Livrable** : Démo live end-to-end de 5 minutes + prototype fonctionnel + vidéo de secours

**Date de validation** : _______________

**Validé par** : _______________

## 1. CONTEXTE ET PROBLÉMATIQUE

### 1.1 Contexte

Yas Togo est l'opérateur télécom n°1 au Togo, avec la marque de paiement mobile **Mixx by Yas**. Sa division **Yas Business** cible les PME togolaises pour vendre :

- **Fibre Pro** : internet très haut débit pour entreprises
- **Flotte mobile** : forfaits SIM groupés pour équipes
- **Mixx Business** : encaissement marchand, virements groupés
- **API SMS** : intégration paiement et communication

### 1.2 Problème

Aujourd'hui, les commerciaux de Yas Business font face à :

- **4 heures par jour** perdues à chercher manuellement des prospects
- Des **données dispersées** dans plusieurs fichiers et outils non centralisés
- Une **qualification subjective** sans critères objectifs
- Des **relances oubliées** et des opportunités perdues
- Aucune **visibilité centralisée** sur l'état du pipeline commercial

### 1.3 Question centrale

> Comment permettre à une équipe commerciale Yas Business d'identifier automatiquement les PME togolaises les plus pertinentes, de les qualifier objectivement, de lancer et suivre la prospection jusqu'à la conversion — le tout dans un seul outil simple, gratuit et explicable ?

## 2. OBJECTIFS DU PROJET

### 2.1 Objectif général

Créer un **copilote commercial** couvrant le parcours complet :

```
Identifier → Qualifier → Prospecter → Relancer → Convertir / Classer
```

### 2.2 Objectifs spécifiques

| #   | Objectif                               | Indicateur de succès                  |
| --- | -------------------------------------- | ------------------------------------- |
| O1  | Identifier des prospects PME au Togo   | ≥ 12 entreprises en base              |
| O2  | Scorer automatiquement leur pertinence | Score 0-100 + raisons explicites      |
| O3  | Générer des messages personnalisés     | Email en français < 100 mots          |
| O4  | Suivre les relances                    | Statut mis à jour, message J+3 simulé |
| O5  | Convertir et transmettre               | Handoff réel via webhook Discord      |
| O6  | Démontrer le gain de temps             | 4h → 15min chiffré et expliqué        |
| O7  | Montrer une architecture robuste       | Backup Google Sheets + vidéo secours  |

## 3. PÉRIMÈTRE

### 3.1 Dans le périmètre (IN)

- Moteur de scoring ICP Yas Business (Python pur)
- Interface Streamlit de démonstration (3 onglets)
- Génération de messages en français via Groq (Llama 3.3)
- Pipeline de statuts (Nouveau → Converti)
- Simulation de relance J+3
- Handoff réel via webhook Discord
- Backup Google Sheets consultable
- Démo live de 5 minutes
- Vidéo de secours enregistrée

### 3.2 Hors périmètre (OUT)

- Connexion réelle au CRM de Yas Togo
- Envoi réel d'emails ou SMS
- Authentification utilisateurs
- Application mobile
- Intégration API officielle Yas/Mixx
- Déploiement en production
- Scraping massif de données

## 4. UTILISATEURS CIBLES

| Utilisateur                 | Besoin principal                      | Usage de l'outil                         |
| --------------------------- | ------------------------------------- | ---------------------------------------- |
| **Commercial Yas Business** | Trouver rapidement les bons prospects | Recherche + scoring + génération message |
| **Responsable commercial**  | Suivre l'activité de l'équipe         | Vue pipeline + statuts                   |
| **Dirigeant Yas**           | Mesurer l'impact                      | Rapport gain de temps                    |
| **Business developer**      | Alimenter le pipeline                 | Import de nouvelles entreprises          |

## 5. ARCHITECTURE TECHNIQUE

### 5.1 Stack retenue (100 % gratuite)

| Couche                         | Outil                            | Rôle                                    |
| ------------------------------ | -------------------------------- | --------------------------------------- |
| **Interface principale**       | Streamlit                        | Python natif, contrôle total, démo live |
| **Base de données principale** | SQLite                           | Local, rapide, zéro configuration       |
| **Base de données backup**     | Google Sheets                    | Montrable au jury, éditable en direct   |
| **Moteur LLM**                 | Groq (`llama-3.3-70b-versatile`) | Génération < 1s, français               |
| **Handoff**                    | Webhook Discord                  | Notification réelle en démo             |
| **Versionnement**              | Git + GitHub                     | Collaboration équipe                    |
| **Vidéo secours**              | OBS / Loom                       | Backup J4                               |

### 5.2 Architecture logique

```
[Dataset CFE Togo - 12 entreprises]
              │
              ▼
        [SQLite local]
              │
              ▼
    [Moteur de scoring Python]
              │
              ▼
    [Interface Streamlit - 3 onglets]
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
[Recherche] [Pipeline] [Handoff]
    │         │         │
    ▼         ▼         ▼
[Scoring]  [Groq]   [Webhook Discord]
              │         │
              ▼         ▼
        [Message]  [Notification]
              │
              ▼
    [Google Sheets backup]
```

### 5.3 Structure des fichiers

```
Telecom-prospect-IA/
├── app.py                  # Interface Streamlit (3 onglets)
├── scoring.py              # Moteur de scoring ICP (Python pur)
├── llm.py                  # Appel Groq pour génération messages
├── database.py             # Gestion SQLite
├── webhook.py              # Envoi Discord handoff
├── data/
│   └── entreprises.csv     # Dataset 12 entreprises togolaises
├── demo/
│   └── demo_script.md      # Script de démo mot pour mot
├── requirements.txt
└── README.md
```

### 5.4 Schéma base de données SQLite

**Table `entreprises`** :

| Champ             | Type    | Description                                 |
| ----------------- | ------- | ------------------------------------------- |
| id                | INTEGER | Clé primaire                                |
| nom               | TEXT    | Nom entreprise                              |
| secteur           | TEXT    | Banque, Logistique, etc.                    |
| localisation      | TEXT    | Lomé, Kara, Tsevié, autres                  |
| effectif          | INTEGER | Nombre de salariés                          |
| signal_croissance | TEXT    | Ouverture agence, recrutement, etc.         |
| site_web          | BOOLEAN | Présence site web                           |
| paiement_en_ligne | BOOLEAN | Paiement détecté                            |
| score             | INTEGER | Score 0-100                                 |
| score_reasons     | TEXT    | Raisons détaillées du score                 |
| statut            | TEXT    | Nouveau, Scoré, Contacté, Relancé, Converti |
| date_contact      | DATE    | Date dernier contact                        |
| message_genere    | TEXT    | Dernier message généré                      |

## 6. MODULES FONCTIONNELS DÉTAILLÉS

### 6.1 Module 1 — IDENTIFIER

**Description** : Rechercher des entreprises togolaises correspondant à l'ICP Yas Business.

**Entrées** :

- Secteur d'activité (liste déroulante : Banque, Assurance, Logistique, Éducation, Informatique, Commerce, Industrie, Agroalimentaire)
- Localisation (Lomé, Kara, Tsevié, autres)
- Taille (1-9, 10-49, 50-250, 250+)

**Sortie** : Tableau des entreprises avec nom, secteur, localisation, effectif, score.

**Source de données** : Dataset CFE Togo simulé (12 entreprises saisies dans SQLite).

**Règle métier** : Si aucun résultat, afficher "Aucune entreprise trouvée — élargir les critères".

### 6.2 Module 2 — QUALIFIER

**Description** : Attribuer un score de pertinence 0-100 à chaque entreprise.

**Grille de scoring (pondération dégressive)** :

#### Critère 1 — Secteur (30 points max)

| Secteur                             | Points | Justification                   |
| ----------------------------------- | ------ | ------------------------------- |
| Banque, Assurance                   | 30     | Haute valeur, besoins Fibre Pro |
| Logistique, Éducation, Informatique | 25     | Cible cœur Yas Business         |
| Commerce, Industrie                 | 15     | Potentiel moyen                 |
| Agroalimentaire, autres             | 5      | Hors cible prioritaire          |

#### Critère 2 — Effectif (25 points max)

| Tranche          | Points | Justification                   |
| ---------------- | ------ | ------------------------------- |
| 50-250 salariés  | 25     | Taille idéale entreprise        |
| 10-49 salariés   | 20     | Taille correcte, fort potentiel |
| 250-500 salariés | 15     | Grande entreprise, cycle long   |
| 1-9 ou 500+      | 5      | Hors cible                      |

#### Critère 3 — Localisation (20 points max)

| Ville  | Points | Justification              |
| ------ | ------ | -------------------------- |
| Lomé   | 20     | Couverture Fibre optimale  |
| Kara   | 15     | Couverture Fibre partielle |
| Autres | 5      | Hors zone prioritaire      |

#### Critère 4 — Signal de croissance (25 points max)

| Signal                    | Points | Justification          |
| ------------------------- | ------ | ---------------------- |
| Signal présent (non vide) | 25     | Indicateur d'expansion |
| Signal absent             | 0      | Aucun signal détecté   |

**Niveaux de qualification** :

| Score  | Statut                       | Action               |
| ------ | ---------------------------- | -------------------- |
| 75-100 | 🔥 QUALIFIÉ HAUTE PRIORITÉ   | Contact immédiat     |
| 50-74  | 🟡 QUALIFIÉ PRIORITÉ MOYENNE | Template + variables |
| 0-49   | ⚪ DISQUALIFIÉ                | Mise en nurture      |

**Contrainte forte** : Chaque point doit être **explicable**. Le champ `score_reasons` liste les raisons :

```
Score : 90/100
+25 Secteur prioritaire (Logistique)
+20 Taille correcte (45 salariés)
+20 Lomé, couverture Fibre optimale
+25 Signal d'expansion : Recrutement informatique
```

### 6.3 Module 3 — PROSPECTER

**Description** : Générer un message de premier contact personnalisé via Groq.

**API** : Groq (`llama-3.3-70b-versatile`)
**Latence cible** : < 1 seconde

**Prompt exact** :

```
Tu es commercial chez Yas Togo, division Yas Business.
Rédige un email de prospection court en français à destination de :

Entreprise : {nom}
Secteur : {secteur}
Ville : {localisation}
Effectif : {effectif} salariés
Signal de croissance : {signal_croissance}

Raisons du score ICP : {score_reasons}

Présente l'offre Yas Business (Fibre Pro, Flotte mobile, API SMS).
Personnalise en citant UNE raison du score.
Maximum 100 mots. Ton professionnel et direct.
Termine par une proposition de rendez-vous.
```

**Sortie attendue** : Email en français, < 100 mots, personnalisé.

**Fallback** : 2 clés API Groq configurées avec bascule automatique.

### 6.4 Module 4 — RELANCER

**Description** : Programmer et simuler une relance.

**Règles** :

- Si statut = "Contacté" et pas de réponse après 3 jours → générer relance
- Message de relance plus court, ton différent
- Démo : relance J+3 pré-générée, affichée sur clic

**Statuts pipeline** :

```
Nouveau → Scoré → Contacté → Relancé → Converti
                                    → Non intéressé
                                    → À relancer plus tard
```

### 6.5 Module 5 — CONVERTIR / CLASSER

**Description** : Clôturer une opportunité et transmettre.

**Actions possibles** :
| Action | Effet | Déclencheur |
|---|---|---|
| Marquer "Converti" | Déclenche handoff Discord | Décision commercial |
| Marquer "Non intéressé" | Archive le prospect | Décision commercial |
| Marquer "À relancer plus tard" | Retour en nurture | Décision commercial |

**Handoff** : Envoi d'une notification réelle via webhook Discord :

```
✅ Prospect converti : {nom}
Transmis au responsable commercial Yas Business
Secteur : {secteur} | Effectif : {effectif} | Ville : {localisation}
Score ICP : {score}/100
Message généré : {message_genere}
```

### 6.6 Module 6 — BACKUP GOOGLE SHEETS

**Description** : Synchronisation avec un Google Sheet consultable.

**Usage** :

- Affichage en direct dans l'onglet "Pipeline" de Streamlit
- Consultable par le jury sur un écran séparé
- Fallback si Streamlit plante

**Contenu** : Mêmes colonnes que la table SQLite.

### 6.7 Module 7 — TABLEAU DE BORD (optionnel si temps)

- Nombre de prospects par statut
- Taux de conversion simulé
- Gain de temps affiché : 4h → 15min

## 7. INTERFACE STREAMLIT — 3 ONGLETS

### 7.1 Onglet 1 — Recherche & Scoring

**Éléments** :

- Filtres : secteur, localisation, effectif
- Bouton "Rechercher"
- Tableau résultats avec score
- Clic sur une ligne → détail du score (4 raisons)

### 7.2 Onglet 2 — Pipeline

**Éléments** :

- Vue kanban des statuts
- Boutons d'action : "Générer message", "Relancer", "Convertir"
- Affichage message généré en temps réel
- Lien vers Google Sheet backup

### 7.3 Onglet 3 — Handoff

**Éléments** :

- Liste des prospects convertis
- Bouton "Transmettre au commercial"
- Envoi webhook Discord + affichage confirmation

## 9. PLANNING DÉTAILLÉ (4 JOURS)

### Jour 1 — Fondations

| Heure   | Tâche                                    | Responsable  |
| ------- | ---------------------------------------- | ------------ |
| 9h-10h  | Setup Git, Streamlit, structure projet   | Dev Python 1 |
| 10h-12h | Saisie dataset CFE Togo (12 entreprises) | Data         |
| 12h-14h | Écriture `scoring.py` + tests            | Dev Python 1 |
| 14h-17h | Écriture `database.py` + SQLite          | Dev Python 2 |
| 17h-18h | Revue ensemble + validation scoring      | Tous         |

**Livrable J1** : Dataset + scoring fonctionnel en ligne de commande.

### Jour 2 — Interface + LLM

| Heure   | Tâche                                  | Responsable  |
| ------- | -------------------------------------- | ------------ |
| 9h-11h  | Interface Streamlit : onglet Recherche | Dev Python 1 |
| 11h-13h | Affichage détaillé du score            | Dev Python 1 |
| 13h-15h | Intégration Groq (`llm.py`)            | Dev Python 2 |
| 15h-17h | Bouton "Générer message" + affichage   | Dev Python 2 |
| 17h-18h | Tests bout-en-bout                     | Tous         |

**Livrable J2** : Interface fonctionnelle avec scoring et génération.

### Jour 3 — Pipeline + Handoff

| Heure   | Tâche                                     | Responsable         |
| ------- | ----------------------------------------- | ------------------- |
| 9h-11h  | Onglet Pipeline + statuts                 | Dev Python 1        |
| 11h-13h | Simulation relance J+3                    | Dev Python 2        |
| 13h-15h | Webhook Discord (`webhook.py`)            | Dev Python 2        |
| 15h-17h | Google Sheets backup                      | Data                |
| 17h-18h | Écriture script démo + slides scalabilité | Scénario + Chiffres |

**Livrable J3** : Prototype complet + script démo rédigé.

### Jour 4 — Répétition + Enregistrement

| Heure   | Tâche                              | Responsable |
| ------- | ---------------------------------- | ----------- |
| 9h-11h  | Répétition 1 + corrections         | Tous        |
| 11h-13h | Enregistrement vidéo secours       | Tous        |
| 13h-15h | Répétition 2 + ajustements         | Tous        |
| 15h-17h | Répétition 3 + finalisation slides | Tous        |
| 17h-18h | Validation finale + checklist      | Tous        |

**Livrable J4** : Démo live prête + vidéo backup.

## 10. DATASET DE TEST (12 ENTREPRISES)

| Nom_Entreprise         | Secteur         | Effectif | Ville  | Signal_Croissance        | Score_Attendu |
| ---------------------- | --------------- | -------- | ------ | ------------------------ | ------------- |
| Ecobank Togo           | Banque          | 150      | Lomé   | Ouverture d'agence       | **100**       |
| Togo Logistique SA     | Logistique      | 45       | Lomé   | Recrutement informatique | **90**        |
| KBE Digital            | Informatique    | 25       | Lomé   | Levée de fonds           | **85**        |
| Clinique de la Paix    | Éducation       | 12       | Kara   | Nouveau site web         | **70**        |
| Assurance Sunu         | Assurance       | 80       | Lomé   | Expansion régionale      | **100**       |
| Togo Telecom Services  | Informatique    | 60       | Lomé   | Nouveau contrat          | **85**        |
| École Internationale   | Éducation       | 30       | Lomé   | Recrutement enseignants  | **80**        |
| Boutique Adidogomé     | Commerce        | 5        | Lomé   | Aucun                    | **45**        |
| Boulangerie de la Paix | Agroalimentaire | 8        | Tsevié | Aucun                    | **15**        |
| Cabinet Conseil Kara   | Conseil         | 15       | Kara   | Nouveau bureau           | **60**        |
| PME Agricole Sud       | Agroalimentaire | 100      | Autres | Aucun                    | **30**        |
| Startup Fintech        | Informatique    | 12       | Lomé   | Levée de fonds           | **75**        |

**Justification de la variance** : Cette distribution permet de démontrer au jury que le scoring **discrimine** réellement (pas tous à 100), que les **seuils** sont pertinents (60 = qualification), et que les **cas limites** sont gérés.

## 11. CODE PYTHON DU SCORING

```python
# scoring.py — Moteur de scoring ICP Yas Business
# Python pur, compatible Pyodide et natif

def score_prospect(company):
    """
    Calcule le score ICP d'une entreprise.
    Retourne (score, reasons, status).
    """
    score = 0
    reasons = []

    sector = company.get("secteur", "")
    employees = int(company.get("effectif", 0))
    city = company.get("localisation", "")
    signal = company.get("signal_croissance", "")

    # Critère 1 - Secteur (30 pts max)
    if sector in ["Banque", "Assurance"]:
        score += 30
        reasons.append(f"Secteur prioritaire haute valeur ({sector})")
    elif sector in ["Logistique", "Éducation", "Informatique"]:
        score += 25
        reasons.append(f"Secteur prioritaire ({sector})")
    elif sector in ["Commerce", "Industrie"]:
        score += 15
        reasons.append(f"Secteur secondaire ({sector})")
    else:
        score += 5
        reasons.append(f"Secteur hors cible ({sector})")

    # Critère 2 - Effectif (25 pts max)
    if 50 <= employees <= 250:
        score += 25
        reasons.append(f"Taille idéale ({employees} salariés)")
    elif 10 <= employees < 50:
        score += 20
        reasons.append(f"Taille correcte ({employees} salariés)")
    elif 250 < employees <= 500:
        score += 15
        reasons.append(f"Grande entreprise ({employees} salariés)")
    else:
        score += 5
        reasons.append(f"Taille inadaptée ({employees} salariés)")

    # Critère 3 - Localisation (20 pts max)
    if city == "Lomé":
        score += 20
        reasons.append("Lomé, couverture Fibre optimale")
    elif city == "Kara":
        score += 15
        reasons.append("Kara, couverture Fibre partielle")
    else:
        score += 5
        reasons.append(f"Hors zone prioritaire ({city})")

    # Critère 4 - Signal de croissance (25 pts max)
    if signal and signal.strip() != "":
        score += 25
        reasons.append(f"Signal d'expansion : {signal}")
    else:
        reasons.append("Aucun signal de croissance détecté")

    # Détermination du statut
    if score >= 75:
        status = "QUALIFIE_HAUTE_PRIORITE"
    elif score >= 60:
        status = "QUALIFIE_PRIORITE_MOYENNE"
    else:
        status = "DISQUALIFIE"

    return score, " | ".join(reasons), status
```

## 12. SCÉNARIO DE DÉMO (5 MINUTES)

### Ouverture (30 secondes)

> "Une PME togolaise perd 4 heures par jour à chercher manuellement des prospects. Yas Business a besoin d'automatiser ce processus. Voici notre copilote, construit en 4 jours, zéro budget."

### Étape 1 — Identifier (1 minute)

- Ouvrir Streamlit, onglet "Recherche"
- Saisir : Logistique + Lomé + 10-49 salariés
- Cliquer "Rechercher"
- Montrer le tableau des résultats

### Étape 2 — Qualifier (1 minute 30)

- Cliquer sur "Togo Logistique SA"
- Afficher **90/100** + détail des 4 raisons :
  - +25 Secteur prioritaire (Logistique)
  - +20 Taille correcte (45 salariés)
  - +20 Lomé, couverture Fibre optimale
  - +25 Signal d'expansion : Recrutement informatique
- Comparer avec "Boulangerie de la Paix" → **15/100**

### Étape 3 — Prospecter (1 minute)

- Cliquer "Générer message"
- Attendre < 2 secondes
- Afficher l'email généré en français
- Lire à voix haute l'email (personnalisé avec "Recrutement informatique")

### Étape 4 — Relancer & Convertir (1 minute)

- Simuler J+3 : montrer le statut "Relancé" avec message de relance
- Cliquer "Converti"
- **Notification Discord apparaît en direct** sur l'écran
- Montrer le message de handoff : "Transmis au responsable commercial Yas Business"

### Clôture (30 secondes)

> "12 prospects traités : avant 4 heures, après 15 minutes. Et chaque décision de l'IA est expliquée par une raison métier."

## 13. SCALABILITY (DISCOURS)

> "Notre moteur traite 10 entreprises en 30 secondes. Pour passer à 1000 :
> 
> **Goulot 1 — SQLite** : limite de concurrence. Solution : migration vers PostgreSQL (1 ligne de changement).
> 
> **Goulot 2 — Groq API** : rate limit gratuit. Solution : score > 75 = génération temps réel ; score < 75 = template + variables.
> 
> **Goulot 3 — Streamlit** : limite de sessions simultanées. Solution : déploiement sur Streamlit Cloud ou migration vers FastAPI + React.
> 
> **Goulot 4 — Webhook Discord** : limite de débit. Solution : file d'attente Redis ou webhook par lots.
> 
> **Goulot 5 — Google Sheets** : limite à ~10 000 lignes. Solution : migration vers Airtable ou PostgreSQL."

## 14. RISQUES ET MITIGATION

| Risque                 | Probabilité | Impact   | Mitigation                                           |
| ---------------------- | ----------- | -------- | ---------------------------------------------------- |
| API Groq saturée       | Moyenne     | Élevé    | 2 clés API + pré-générer 3 messages + vidéo backup   |
| Manque de temps J3     | Moyenne     | Élevé    | Prioriser scoring + génération, abandonner dashboard |
| Débutants bloqués      | Élevée      | Moyen    | Binômes débutant + dev Python                        |
| Démo live échoue       | Faible      | Critique | Vidéo enregistrée J4 + fallback Google Sheets        |
| Dataset insuffisant    | Faible      | Moyen    | 12 entreprises minimum saisies                       |
| Webhook Discord échoue | Faible      | Moyen    | Fallback notification dans Streamlit                 |

## 15. CRITÈRES D'ÉVALUATION (alignés fiche projet)

| Critère                             | Poids | Réponse                                          |
| ----------------------------------- | ----- | ------------------------------------------------ |
| Pertinence des prospects identifiés | 20 %  | Dataset 12 entreprises togolaises réalistes      |
| Qualité de la qualification         | 20 %  | Scoring 4 dimensions + explication détaillée     |
| Fluidité du parcours commercial     | 15 %  | Pipeline 5 statuts visible dans Streamlit        |
| Automatisation                      | 15 %  | Scoring auto + génération Groq + webhook Discord |
| Facilité d'utilisation              | 10 %  | Interface Streamlit simple, 3 onglets            |
| Pertinence de l'IA                  | 10 %  | Groq Llama 3.3 + scoring explicable              |
| Impact potentiel sur les ventes     | 10 %  | 4h → 15min chiffré et démontré                   |

## 16. LIVRABLES

| #   | Livrable               | Format           | Échéance |
| --- | ---------------------- | ---------------- | -------- |
| L1  | Dataset 12 entreprises | CSV + SQLite     | J1       |
| L2  | Moteur de scoring      | `scoring.py`     | J1       |
| L3  | Interface Streamlit    | `app.py`         | J2       |
| L4  | Module LLM             | `llm.py`         | J2       |
| L5  | Pipeline statuts       | Intégré `app.py` | J3       |
| L6  | Webhook Discord        | `webhook.py`     | J3       |
| L7  | Google Sheets backup   | Sheet partagé    | J3       |
| L8  | Script démo            | `demo_script.md` | J3       |
| L9  | Vidéo secours          | MP4 4K           | J4       |
| L10 | Slides scalabilité     | PDF              | J4       |

## 17. CHECKLIST AVANT DÉMO

- [ ] Interface Streamlit se lance sans erreur
- [ ] Recherche retourne ≥ 5 entreprises
- [ ] Score affiché avec détail des 4 raisons
- [ ] Message généré en < 5 secondes
- [ ] Pipeline 5 statuts fonctionnel
- [ ] Webhook Discord envoie la notification
- [ ] Google Sheets backup accessible
- [ ] Vidéo secours enregistrée et testée
- [ ] Script démo répété 3 fois
- [ ] Slides scalabilité prêtes
- [ ] Chiffres 4h→15min justifiés
- [ ] 2 clés API Groq configurées

## 18. PROCHAINES ÉTAPES

1. **Valider ce cahier des charges** avec l'équipe
2. **Créer le repo Git** et la structure de fichiers
3. **Saisir le dataset** 12 entreprises (Jour 1 matin)
4. **Coder `scoring.py`** en priorité absolue
5. **Tester chaque module** avant de passer au suivant
6. **Configurer le webhook Discord** (Jour 3)
7. **Répéter la démo** au moins 3 fois avant J4

**Document validé le** : _______________

**Par** : _______________

**Équipe** : _______________
