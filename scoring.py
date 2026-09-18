# scoring.py — Moteur de scoring ICP Opticom Business
# Python pur — aucune dépendance externe

def score_prospect(company: dict) -> tuple[int, str, str]:
    """
    Calcule le score ICP d'une entreprise (0-100).

    Args:
        company: dict avec les clés secteur, effectif, localisation, signal_croissance

    Returns:
        (score, score_reasons, statut)
        - score       : entier 0-100
        - score_reasons : chaîne des raisons séparées par " | "
        - statut      : "QUALIFIE_HAUTE_PRIORITE" | "QUALIFIE_PRIORITE_MOYENNE" | "DISQUALIFIE"
    """
    score = 0
    reasons = []

    secteur   = company.get("secteur", "").strip()
    effectif  = int(company.get("effectif", 0))
    ville     = company.get("localisation", "").strip()
    signal    = company.get("signal_croissance", "")
    if signal is None:
        signal = ""
    signal = str(signal).strip()

    # ── Critère 1 — Secteur (30 pts max) ──────────────────────────────────
    if secteur in ["Banque", "Assurance"]:
        score += 30
        reasons.append(f"Secteur prioritaire haute valeur ({secteur})")
    elif secteur in ["Logistique", "Éducation", "Informatique"]:
        score += 25
        reasons.append(f"Secteur prioritaire ({secteur})")
    elif secteur in ["Commerce", "Industrie"]:
        score += 15
        reasons.append(f"Secteur secondaire ({secteur})")
    else:
        score += 5
        reasons.append(f"Secteur hors cible ({secteur})")

    # ── Critère 2 — Effectif (25 pts max) ─────────────────────────────────
    if 50 <= effectif <= 250:
        score += 25
        reasons.append(f"Taille idéale ({effectif} salariés)")
    elif 10 <= effectif < 50:
        score += 20
        reasons.append(f"Taille correcte ({effectif} salariés)")
    elif 250 < effectif <= 500:
        score += 15
        reasons.append(f"Grande entreprise ({effectif} salariés)")
    else:
        score += 5
        reasons.append(f"Taille inadaptée ({effectif} salariés)")

    # ── Critère 3 — Localisation (20 pts max) ─────────────────────────────
    if ville == "Lomé":
        score += 20
        reasons.append("Lomé, couverture Fibre optimale")
    elif ville == "Kara":
        score += 15
        reasons.append("Kara, couverture Fibre partielle")
    else:
        score += 5
        reasons.append(f"Hors zone prioritaire ({ville})")

    # ── Critère 4 — Signal de croissance (25 pts max) ─────────────────────
    if signal and signal.lower() not in ["", "aucun", "nan"]:
        score += 25
        reasons.append(f"Signal d'expansion : {signal}")
    else:
        reasons.append("Aucun signal de croissance détecté")

    # ── Statut de qualification ────────────────────────────────────────────
    if score >= 75:
        statut = "QUALIFIE_HAUTE_PRIORITE"
    elif score >= 50:
        statut = "QUALIFIE_PRIORITE_MOYENNE"
    else:
        statut = "DISQUALIFIE"

    score_reasons = " | ".join(reasons)
    return score, score_reasons, statut


def format_score_display(score: int, reasons: str, statut: str) -> str:
    """Formate le score pour affichage lisible (CLI ou Streamlit)."""
    labels = {
        "QUALIFIE_HAUTE_PRIORITE":  "🔥 QUALIFIÉ HAUTE PRIORITÉ",
        "QUALIFIE_PRIORITE_MOYENNE": "🟡 QUALIFIÉ PRIORITÉ MOYENNE",
        "DISQUALIFIE":               "⚪ DISQUALIFIÉ",
    }
    lines = [f"Score : {score}/100 — {labels.get(statut, statut)}"]
    for r in reasons.split(" | "):
        lines.append(f"  • {r}")
    return "\n".join(lines)


# ── Tests CLI ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Dataset des 12 entreprises avec scores attendus
    dataset = [
        {"nom": "Ecobank Togo",              "secteur": "Banque",          "effectif": 150, "localisation": "Lomé",    "signal_croissance": "Ouverture d'une agence entreprise à Agoè",                     "score_attendu": 100},
        {"nom": "Togo Logistique SA",         "secteur": "Logistique",      "effectif": 45,  "localisation": "Lomé",    "signal_croissance": "Recrutement de deux profils informatique pour la traçabilité", "score_attendu": 90},
        {"nom": "KBE Digital",                "secteur": "Informatique",    "effectif": 25,  "localisation": "Lomé",    "signal_croissance": "Levée de fonds d'amorçage pour développer une plateforme SaaS","score_attendu": 90},
        {"nom": "Clinique de la Paix",        "secteur": "Éducation",       "effectif": 12,  "localisation": "Kara",    "signal_croissance": "Nouveau portail de prise de rendez-vous en ligne",             "score_attendu": 85},
        {"nom": "Assurance Sunu",             "secteur": "Assurance",       "effectif": 80,  "localisation": "Lomé",    "signal_croissance": "Extension régionale de son réseau d'agences",                  "score_attendu": 100},
        {"nom": "Togo Telecom Services",      "secteur": "Informatique",    "effectif": 60,  "localisation": "Lomé",    "signal_croissance": "Nouveau contrat de maintenance multi-sites",                   "score_attendu": 95},
        {"nom": "École Internationale",       "secteur": "Éducation",       "effectif": 30,  "localisation": "Lomé",    "signal_croissance": "Recrutement d'enseignants et ouverture d'une section bilingue","score_attendu": 90},
        {"nom": "Boutique Adidogomé",         "secteur": "Commerce",        "effectif": 5,   "localisation": "Lomé",    "signal_croissance": "",                                                             "score_attendu": 40},
        {"nom": "Boulangerie de la Paix",     "secteur": "Agroalimentaire", "effectif": 8,   "localisation": "Tsevié",  "signal_croissance": "",                                                             "score_attendu": 15},
        {"nom": "Cabinet Conseil Kara",       "secteur": "Conseil",         "effectif": 15,  "localisation": "Kara",    "signal_croissance": "Nouveau bureau de conseil RH ouvert à Kara",                  "score_attendu": 65},
        {"nom": "PME Agricole Sud",           "secteur": "Agroalimentaire", "effectif": 100, "localisation": "Kpalimé", "signal_croissance": "",                                                             "score_attendu": 35},
        {"nom": "Startup Fintech",            "secteur": "Informatique",    "effectif": 12,  "localisation": "Lomé",    "signal_croissance": "Levée de fonds pré-seed pour intégrer de nouveaux marchands",  "score_attendu": 90},
    ]

    print("=" * 65)
    print("  SCORING ICP — CibleNet (Opticom Business)")
    print("=" * 65)

    all_passed = True
    for company in dataset:
        score, reasons, statut = score_prospect(company)
        attendu = company["score_attendu"]
        ok = "✅" if score == attendu else "❌"
        if score != attendu:
            all_passed = False

        print(f"\n{ok} {company['nom']}")
        print(f"   Score obtenu : {score}/100  |  Attendu : {attendu}/100")
        print(f"   Statut : {statut}")
        print(f"   Raisons :")
        for r in reasons.split(" | "):
            print(f"     • {r}")

    print("\n" + "=" * 65)
    if all_passed:
        print("✅ TOUS LES SCORES VALIDES — moteur prêt")
    else:
        print("❌ Certains scores ne correspondent pas aux valeurs attendues")
    print("=" * 65)
