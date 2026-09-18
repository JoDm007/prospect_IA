# CibleNet

Copilote commercial pour Opticom Business / Opticom Togo.  
Identifie, qualifie et aide à convertir les meilleures PME togolaises — zéro budget, 100 % Python.

## Stack

| Couche | Outil |
|---|---|
| Interface | Streamlit |
| Base de données | SQLite |
| Backup | Google Sheets |
| LLM | Groq — llama-3.3-70b-versatile |
| Handoff | Webhook Discord |

## Structure

```
Prospect_IA/
├── app.py              # Interface Streamlit (3 onglets)
├── scoring.py          # Moteur de scoring ICP (Python pur)
├── llm.py              # Appel Groq — génération de messages
├── database.py         # Gestion SQLite
├── webhook.py          # Handoff Discord
├── data/
│   ├── entreprises.csv           # Dataset 12 entreprises
│   ├── messages_simules.csv      # Messages pré-générés
│   └── relances_j3_simulees.csv  # Relances J+3 simulées
├── demo/
│   └── demo_script.md  # Script de démo mot pour mot
├── requirements.txt
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

## Variables d'environnement à configurer

Créer un fichier `.env` (ne pas committer) :

```
GROQ_API_KEY_1=votre_cle_groq_principale
GROQ_API_KEY_2=votre_cle_groq_backup
DISCORD_WEBHOOK_URL=votre_url_webhook_discord
GOOGLE_SHEETS_ID=votre_id_google_sheet
```

## Validation scoring en CLI

```bash
python scoring.py
```

## Équipe

5 personnes — 4 jours — 0 FCFA
