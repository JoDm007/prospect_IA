# llm.py — Génération de messages via Groq (Llama 3.3-70b)
# Gère le fallback automatique entre 2 clés API

import os

# Chargement .env manuel (sans dépendance python-dotenv)
def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()

# ── Clés API (lues depuis l'environnement) ────────────────────────────────────
GROQ_API_KEY_1 = os.environ.get("GROQ_API_KEY_1", "")
GROQ_API_KEY_2 = os.environ.get("GROQ_API_KEY_2", "")
MODEL           = "qwen/qwen3.8-27b"  # Modèle disponible sur ce compte Groq


def _call_groq(prompt: str, api_key: str) -> str:
    """
    Appel bas-niveau à l'API Groq via le SDK officiel.
    Lève une exception si la clé est absente ou si l'API répond une erreur.
    """
    if not api_key:
        raise ValueError("Clé API Groq absente.")

    from groq import Groq  # import local pour ne pas planter si non installé
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=400,
        reasoning_effort="none",  # Désactive le mode "thinking" de Qwen
    )
    content = response.choices[0].message.content.strip()
    # Supprime les balises <think>...</think> si présentes
    import re
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    return content


def _call_with_fallback(prompt: str) -> tuple[str, bool]:
    """
    Essaie la clé principale, puis la clé backup si échec.
    Relit les clés depuis l'environnement à chaque appel.

    Returns:
        (message généré, used_fallback)
    """
    _load_env()
    key1 = os.environ.get("GROQ_API_KEY_1", "")
    key2 = os.environ.get("GROQ_API_KEY_2", "")
    try:
        return _call_groq(prompt, key1), False
    except Exception as e1:
        print(f"[LLM] Clé principale échouée ({e1}). Bascule sur clé backup...")
        try:
            return _call_groq(prompt, key2), True
        except Exception as e2:
            raise RuntimeError(
                f"Les deux clés API Groq ont échoué.\n  Clé 1 : {e1}\n  Clé 2 : {e2}"
            )


# ── Prompt de premier contact ─────────────────────────────────────────────────

PROMPT_PREMIER_CONTACT = """Tu es commercial chez Yas Togo, division Yas Business.
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
Réponds uniquement avec le corps de l'email, sans objet ni signature."""

# ── Prompt de relance J+3 ─────────────────────────────────────────────────────

PROMPT_RELANCE = """Tu es commercial chez Yas Togo, division Yas Business.
Tu relances un prospect qui n'a pas répondu à ton premier contact il y a 3 jours.

Entreprise : {nom}
Secteur : {secteur}
Ville : {localisation}
Message initial envoyé : {message_initial}

Rédige un court email de relance en français.
Ton plus direct et plus bref que le premier message.
Maximum 60 mots. Propose un créneau concret (jour de la semaine).
Réponds uniquement avec le corps de l'email, sans objet ni signature."""


# ── Fonctions publiques ───────────────────────────────────────────────────────

def generer_message_prospect(entreprise: dict) -> tuple[str, bool]:
    """
    Génère un email de premier contact personnalisé pour une entreprise.

    Args:
        entreprise : dict avec les champs nom, secteur, localisation,
                     effectif, signal_croissance, score_reasons

    Returns:
        (message, used_fallback)
    """
    prompt = PROMPT_PREMIER_CONTACT.format(
        nom               = entreprise.get("nom", ""),
        secteur           = entreprise.get("secteur", ""),
        localisation      = entreprise.get("localisation", ""),
        effectif          = entreprise.get("effectif", ""),
        signal_croissance = entreprise.get("signal_croissance", "Aucun"),
        score_reasons     = entreprise.get("score_reasons", ""),
    )
    return _call_with_fallback(prompt)


def generer_relance(entreprise: dict) -> tuple[str, bool]:
    """
    Génère un message de relance J+3 pour un prospect déjà contacté.

    Args:
        entreprise : dict avec nom, secteur, localisation, message_genere

    Returns:
        (message_relance, used_fallback)
    """
    prompt = PROMPT_RELANCE.format(
        nom             = entreprise.get("nom", ""),
        secteur         = entreprise.get("secteur", ""),
        localisation    = entreprise.get("localisation", ""),
        message_initial = entreprise.get("message_genere", ""),
    )
    return _call_with_fallback(prompt)


def groq_disponible() -> bool:
    """Vérifie si au moins une clé API Groq est configurée.
    Relit le .env à chaque appel pour éviter les problèmes de cache Streamlit."""
    _load_env()
    k1 = os.environ.get("GROQ_API_KEY_1", "")
    k2 = os.environ.get("GROQ_API_KEY_2", "")
    return bool(k1 or k2)


# ── Messages simulés (fallback si Groq indisponible en démo) ─────────────────

def get_message_simule(entreprise: dict, type_message: str = "premier_contact") -> str:
    """
    Retourne un message pré-rédigé depuis les CSV de simulation.
    Utilisé comme fallback si Groq est indisponible.
    """
    import csv, os
    base = os.path.dirname(os.path.abspath(__file__))

    if type_message == "relance":
        fichier = os.path.join(base, "data", "relances_j3_simulees.csv")
        id_col  = "entreprise_id"
        msg_col = "contenu"
    else:
        fichier = os.path.join(base, "data", "messages_simules.csv")
        id_col  = "entreprise_id"
        msg_col = "contenu"

    try:
        with open(fichier, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if int(row[id_col]) == int(entreprise.get("id", -1)):
                    return row[msg_col]
    except Exception:
        pass

    # Fallback générique si rien trouvé
    return (
        f"Bonjour, nous souhaiterions vous présenter les offres Yas Business "
        f"(Fibre Pro, Flotte mobile, API SMS) adaptées à {entreprise.get('nom', 'votre entreprise')}. "
        f"Seriez-vous disponible pour un échange de 20 minutes cette semaine ?"
    )


# ── CLI de test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST llm.py — Yas Prospect Copilot")
    print("=" * 60)

    if not groq_disponible():
        print("\n⚠️  Aucune clé API Groq configurée dans .env")
        print("   → Test avec message simulé (fallback CSV)\n")
        test = {
            "id": 2,
            "nom": "Togo Logistique SA",
            "secteur": "Logistique",
            "localisation": "Lomé",
            "effectif": 45,
            "signal_croissance": "Recrutement de deux profils informatique pour la traçabilité",
            "score_reasons": "Secteur prioritaire (Logistique) | Taille correcte (45 salariés) | Lomé, couverture Fibre optimale | Signal d'expansion",
            "message_genere": "",
        }
        print("── Message simulé (premier contact) ──")
        print(get_message_simule(test, "premier_contact"))
        print("\n── Message simulé (relance J+3) ──")
        print(get_message_simule(test, "relance"))
    else:
        print("\n✅ Clé(s) API Groq détectée(s). Test de génération en cours...\n")
        test = {
            "nom": "Togo Logistique SA",
            "secteur": "Logistique",
            "localisation": "Lomé",
            "effectif": 45,
            "signal_croissance": "Recrutement de deux profils informatique pour la traçabilité",
            "score_reasons": "Secteur prioritaire (Logistique) | Taille correcte (45 salariés) | Lomé, couverture Fibre optimale | Signal d'expansion",
            "message_genere": "",
        }
        try:
            msg, fallback = generer_message_prospect(test)
            print(f"── Email généré {'(via clé backup)' if fallback else '(clé principale)'} ──")
            print(msg)
        except RuntimeError as e:
            print(f"❌ Erreur : {e}")

    print("\n" + "=" * 60)
