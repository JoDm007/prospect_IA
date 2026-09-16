# webhook.py — Handoff Discord via webhook
# Envoie une notification réelle quand un prospect est converti

import os
import json
import urllib.request
import urllib.error

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

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")


def envoyer_handoff(entreprise: dict) -> tuple[bool, str]:
    """
    Envoie une notification Discord de handoff pour un prospect converti.

    Args:
        entreprise : dict avec les champs du prospect converti

    Returns:
        (succès, message_detail)
        - succès         : True si Discord a bien reçu la notification
        - message_detail : description du résultat ou de l'erreur
    """
    if not DISCORD_WEBHOOK_URL:
        # Pas de webhook configuré → fallback silencieux (utile en démo)
        print("[WEBHOOK] Aucune URL Discord configurée — handoff simulé.")
        return True, "Handoff simulé (pas de webhook configuré)"

    # ── Construction du message Discord ──────────────────────────────────────
    nom       = entreprise.get("nom", "Inconnu")
    secteur   = entreprise.get("secteur", "-")
    effectif  = entreprise.get("effectif", "-")
    ville     = entreprise.get("localisation", "-")
    score     = entreprise.get("score", 0)
    message   = entreprise.get("message_genere", "")

    # Troncature du message pour Discord (limite 1024 chars par champ embed)
    message_court = message[:300] + "..." if len(message) > 300 else message

    payload = {
        "username": "Yas Prospect Copilot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
        "embeds": [
            {
                "title": f"✅ Prospect converti : {nom}",
                "description": "Transmis au responsable commercial Yas Business",
                "color": 3066993,  # vert Discord
                "fields": [
                    {"name": "Secteur",      "value": secteur,         "inline": True},
                    {"name": "Effectif",     "value": str(effectif),   "inline": True},
                    {"name": "Ville",        "value": ville,            "inline": True},
                    {"name": "Score ICP",    "value": f"{score}/100",   "inline": True},
                    {"name": "Message envoyé", "value": message_court or "—", "inline": False},
                ],
                "footer": {"text": "Yas Business · Yas Prospect Copilot"},
            }
        ],
    }

    # ── Envoi HTTP (urllib stdlib, pas de requests requis) ────────────────────
    try:
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data    = data,
            headers = {
                "Content-Type": "application/json",
                "User-Agent":   "YasProspectCopilot/1.0",
            },
            method  = "POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            # Discord renvoie 204 No Content si succès
            if resp.status in (200, 204):
                print(f"[WEBHOOK] Handoff envoyé pour {nom} (HTTP {resp.status})")
                return True, f"Notification Discord envoyée (HTTP {resp.status})"
            else:
                return False, f"Discord a répondu HTTP {resp.status}"

    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        print(f"[WEBHOOK] Erreur HTTP {e.code} : {detail}")
        return False, f"Erreur HTTP {e.code} : {detail[:200]}"

    except urllib.error.URLError as e:
        print(f"[WEBHOOK] Erreur réseau : {e.reason}")
        return False, f"Erreur réseau : {e.reason}"

    except Exception as e:
        print(f"[WEBHOOK] Erreur inattendue : {e}")
        return False, str(e)


# ── CLI de test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  TEST webhook.py — Yas Prospect Copilot")
    print("=" * 55)

    test = {
        "id":             1,
        "nom":            "Ecobank Togo",
        "secteur":        "Banque",
        "effectif":       150,
        "localisation":   "Lomé",
        "score":          100,
        "message_genere": "Bonjour, l'ouverture de votre agence à Agoè confirme la dynamique d'Ecobank Togo. Yas Business peut sécuriser cette expansion avec Fibre Pro, flotte mobile et API SMS. Seriez-vous disponible cette semaine ?",
    }

    if not DISCORD_WEBHOOK_URL:
        print("\n⚠️  DISCORD_WEBHOOK_URL non configurée dans .env")
        print("   Ajoutez cette ligne dans votre fichier .env :")
        print("   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        print("\n   Test simulé (sans envoi réel) :")
        ok, detail = envoyer_handoff(test)
        print(f"   Résultat : ok={ok}, detail={detail}")
    else:
        print(f"\n✅ URL Discord détectée. Envoi du handoff test...")
        ok, detail = envoyer_handoff(test)
        if ok:
            print(f"✅ Succès : {detail}")
        else:
            print(f"❌ Échec : {detail}")

    print("=" * 55)
