# notifier.py — Canaux de notification multicanal
# Gmail (SMTP) | WhatsApp (Twilio) | SMS (Twilio)
# Chaque canal est indépendant et s'active via .env

import os
import smtplib
import ssl
from email.mime.text       import MIMEText
from email.mime.multipart  import MIMEMultipart

# ── Chargement .env ───────────────────────────────────────────────────────────
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

# ── Credentials (lus depuis .env) ─────────────────────────────────────────────
GMAIL_SENDER        = os.environ.get("GMAIL_SENDER", "")
GMAIL_APP_PASSWORD  = os.environ.get("GMAIL_APP_PASSWORD", "")
GMAIL_RECIPIENT     = os.environ.get("GMAIL_RECIPIENT", "")

TWILIO_ACCOUNT_SID    = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN     = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM  = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_WHATSAPP_TO    = os.environ.get("TWILIO_WHATSAPP_TO", "")
TWILIO_SMS_FROM       = os.environ.get("TWILIO_SMS_FROM", "")
TWILIO_SMS_TO         = os.environ.get("TWILIO_SMS_TO", "")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _construire_objet(entreprise: dict, type_msg: str = "contact") -> str:
    """Génère l'objet de l'email selon le type de message."""
    nom = entreprise.get("nom", "votre entreprise")
    if type_msg == "relance":
        return f"Relance — Proposition Opticom Business pour {nom}"
    elif type_msg == "handoff":
        return f"✅ Prospect converti : {nom} — Handoff Opticom Business"
    else:
        return f"Proposition Opticom Business pour {nom}"


def _construire_corps_html(entreprise: dict, message: str) -> str:
    """Construit un email HTML propre à partir du message texte."""
    nom      = entreprise.get("nom", "")
    secteur  = entreprise.get("secteur", "")
    score    = entreprise.get("score", 0)
    ville    = entreprise.get("localisation", "")

    # Convertit les sauts de ligne en <br>
    message_html = message.replace("\n", "<br>")

    return f"""
    <html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;">
      <div style="background:#0047AB;padding:16px 24px;border-radius:8px 8px 0 0;">
        <h2 style="color:white;margin:0;">Opticom Business — CibleNet</h2>
      </div>
      <div style="padding:24px;border:1px solid #ddd;border-top:none;border-radius:0 0 8px 8px;">
        <p style="font-size:0.9rem;color:#666;">
          Prospect : <strong>{nom}</strong> &nbsp;|&nbsp;
          Secteur : <strong>{secteur}</strong> &nbsp;|&nbsp;
          Ville : <strong>{ville}</strong> &nbsp;|&nbsp;
          Score ICP : <strong>{score}/100</strong>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:16px 0;">
        <p style="font-size:1rem;line-height:1.6;">{message_html}</p>
        <hr style="border:none;border-top:1px solid #eee;margin:16px 0;">
        <p style="font-size:0.8rem;color:#999;">
          Message généré par CibleNet · Opticom Business Togo
        </p>
      </div>
    </body></html>
    """


# ── CANAL 1 — GMAIL ───────────────────────────────────────────────────────────

def gmail_disponible() -> bool:
    return bool(GMAIL_SENDER and GMAIL_APP_PASSWORD and GMAIL_RECIPIENT)


def envoyer_gmail(entreprise: dict, message: str,
                  type_msg: str = "contact",
                  destinataire: str = "") -> tuple[bool, str]:
    """
    Envoie un email via SMTP Gmail.

    Args:
        entreprise   : dict du prospect
        message      : corps du message (texte brut, potentiellement modifié)
        type_msg     : "contact" | "relance" | "handoff"
        destinataire : adresse email cible (utilise GMAIL_RECIPIENT si vide)

    Returns:
        (succès, détail)
    """
    if not gmail_disponible():
        return False, "Credentials Gmail non configurés dans .env"

    to_addr = destinataire.strip() if destinataire.strip() else GMAIL_RECIPIENT
    objet   = _construire_objet(entreprise, type_msg)

    # Construction email multipart (texte + HTML)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = objet
    msg["From"]    = GMAIL_SENDER
    msg["To"]      = to_addr

    msg.attach(MIMEText(message, "plain", "utf-8"))
    msg.attach(MIMEText(_construire_corps_html(entreprise, message), "html", "utf-8"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, to_addr, msg.as_string())
        print(f"[GMAIL] Email envoyé à {to_addr} pour {entreprise.get('nom')}")
        return True, f"Email envoyé à {to_addr}"

    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification Gmail — vérifier GMAIL_APP_PASSWORD dans .env"
    except smtplib.SMTPException as e:
        return False, f"Erreur SMTP : {e}"
    except Exception as e:
        return False, f"Erreur inattendue Gmail : {e}"


# ── CANAL 2 — WHATSAPP (Twilio Sandbox) ──────────────────────────────────────

def whatsapp_disponible() -> bool:
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_TO)


def envoyer_whatsapp(entreprise: dict, message: str,
                     type_msg: str = "contact") -> tuple[bool, str]:
    """
    Envoie un message WhatsApp via le Twilio Sandbox.

    Args:
        entreprise : dict du prospect
        message    : corps du message
        type_msg   : "contact" | "relance" | "handoff"

    Returns:
        (succès, détail)
    """
    if not whatsapp_disponible():
        return False, "Credentials Twilio WhatsApp non configurés dans .env"

    try:
        from twilio.rest import Client
    except ImportError:
        return False, "SDK Twilio non installé — lancer : pip install twilio"

    # Préfixe contextuel selon le type
    prefixes = {
        "contact": "📋 *Nouveau prospect — Opticom Business*\n\n",
        "relance": "🔁 *Relance J+3 — Opticom Business*\n\n",
        "handoff": "✅ *Prospect converti — Handoff Opticom Business*\n\n",
    }
    nom    = entreprise.get("nom", "")
    score  = entreprise.get("score", 0)
    footer = f"\n\n---\n🏢 {nom} | Score ICP : {score}/100"
    corps  = prefixes.get(type_msg, "") + message + footer

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            from_ = TWILIO_WHATSAPP_FROM,
            to    = TWILIO_WHATSAPP_TO,
            body  = corps,
        )
        print(f"[WHATSAPP] Message envoyé : SID={msg.sid} pour {nom}")
        return True, f"WhatsApp envoyé (SID : {msg.sid})"

    except Exception as e:
        err = str(e)
        if "21408" in err or "sandbox" in err.lower():
            return False, "Numéro non inscrit au Twilio Sandbox. Envoyer 'join <code>' au +14155238886 depuis WhatsApp."
        return False, f"Erreur Twilio WhatsApp : {err}"


# ── CANAL 3 — SMS (Twilio) ────────────────────────────────────────────────────

def sms_disponible() -> bool:
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
                and TWILIO_SMS_FROM and TWILIO_SMS_TO)


def envoyer_sms(entreprise: dict, message: str,
                type_msg: str = "contact") -> tuple[bool, str]:
    """
    Envoie un SMS via Twilio.

    Args:
        entreprise : dict du prospect
        message    : corps du message (sera tronqué à 160 chars si nécessaire)
        type_msg   : "contact" | "relance" | "handoff"

    Returns:
        (succès, détail)
    """
    if not sms_disponible():
        return False, "Credentials Twilio SMS non configurés dans .env"

    try:
        from twilio.rest import Client
    except ImportError:
        return False, "SDK Twilio non installé — lancer : pip install twilio"

    # SMS : message court (160 chars max pour un seul segment)
    nom   = entreprise.get("nom", "")
    corps = f"Opticom Business : {message[:130]}... — {nom}"
    if len(corps) > 160:
        corps = corps[:157] + "..."

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            from_ = TWILIO_SMS_FROM,
            to    = TWILIO_SMS_TO,
            body  = corps,
        )
        print(f"[SMS] SMS envoyé : SID={msg.sid} pour {nom}")
        return True, f"SMS envoyé (SID : {msg.sid})"

    except Exception as e:
        return False, f"Erreur Twilio SMS : {str(e)}"


# ── BROADCAST — Tous les canaux actifs ────────────────────────────────────────

def envoyer_tous(entreprise: dict, message: str,
                 type_msg: str = "contact",
                 canaux: list[str] | None = None) -> dict[str, tuple[bool, str]]:
    """
    Envoie sur tous les canaux actifs (ou ceux spécifiés dans `canaux`).

    Args:
        entreprise : dict du prospect
        message    : message (potentiellement modifié par l'utilisateur)
        type_msg   : "contact" | "relance" | "handoff"
        canaux     : liste de canaux ["gmail","whatsapp","sms"] ou None = tous

    Returns:
        Dict { canal: (succès, détail) }
    """
    from webhook import envoyer_handoff

    resultats = {}
    cibles = canaux or ["discord", "gmail", "whatsapp", "sms"]

    if "discord" in cibles:
        resultats["discord"] = envoyer_handoff(entreprise)

    if "gmail" in cibles and gmail_disponible():
        resultats["gmail"] = envoyer_gmail(entreprise, message, type_msg)

    if "whatsapp" in cibles and whatsapp_disponible():
        resultats["whatsapp"] = envoyer_whatsapp(entreprise, message, type_msg)

    if "sms" in cibles and sms_disponible():
        resultats["sms"] = envoyer_sms(entreprise, message, type_msg)

    return resultats


# ── Statut des canaux configurés ──────────────────────────────────────────────

def canaux_actifs() -> dict[str, bool]:
    """Retourne l'état de configuration de chaque canal."""
    from webhook import DISCORD_WEBHOOK_URL
    return {
        "discord":  bool(DISCORD_WEBHOOK_URL),
        "gmail":    gmail_disponible(),
        "whatsapp": whatsapp_disponible(),
        "sms":      sms_disponible(),
    }


# ── CLI de test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 58)
    print("  TEST notifier.py — Canaux de notification")
    print("=" * 58)

    actifs = canaux_actifs()
    print("\nCanaux configurés :")
    for canal, ok in actifs.items():
        print(f"  {'✅' if ok else '⚠️ '} {canal:<12} {'Actif' if ok else 'Non configuré'}")

    test = {
        "id": 2, "nom": "Togo Logistique SA", "secteur": "Logistique",
        "effectif": 45, "localisation": "Lomé", "score": 90,
        "message_genere": (
            "Bonjour, votre recrutement pour la traçabilité montre que Togo Logistique SA "
            "accélère sa digitalisation. Opticom Business peut relier vos équipes avec Fibre Pro, "
            "flotte mobile et API SMS. Auriez-vous 20 minutes cette semaine ?"
        ),
    }
    message_test = test["message_genere"]

    print()
    if actifs.get("gmail"):
        print("── Test Gmail ──")
        ok, detail = envoyer_gmail(test, message_test, "contact")
        print(f"  {'✅' if ok else '❌'} {detail}")

    if actifs.get("whatsapp"):
        print("── Test WhatsApp ──")
        ok, detail = envoyer_whatsapp(test, message_test, "contact")
        print(f"  {'✅' if ok else '❌'} {detail}")

    if actifs.get("sms"):
        print("── Test SMS ──")
        ok, detail = envoyer_sms(test, message_test, "contact")
        print(f"  {'✅' if ok else '❌'} {detail}")

    if not any(actifs.values()):
        print("\n⚠️  Aucun canal configuré — remplir les variables dans .env")

    print("=" * 58)
