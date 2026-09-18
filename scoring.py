# scoring.py — Moteur de scoring ICP Opticom Business
# Python pur — aucune dépendance externe

def score_prospect(company: dict, settings: dict = None) -> tuple[int, str, str]:
    """
    Calcule le score ICP d'une entreprise (0-100).
    """
    if settings is None:
        from database import get_settings
        settings = get_settings()

    score = 0
    reasons = []

    secteur   = company.get("secteur", "").strip()
    effectif  = int(company.get("effectif", 0))
    ville     = company.get("localisation", "").strip()
    signal    = company.get("signal_croissance", "")
    if signal is None:
        signal = ""
    signal = str(signal).strip()

    grille_sec = settings.get("grille_secteurs", {})
    grille_eff = settings.get("grille_effectif", {})
    grille_loc = settings.get("grille_localisation", {})
    grille_sig = settings.get("grille_signal", {})

    # ── Critère 1 — Secteur ───────────────────────────────────────────────
    if secteur in grille_sec.get("haute_valeur", []):
        score += grille_sec.get("pts_haute", 30)
        reasons.append(f"Secteur prioritaire haute valeur ({secteur})")
    elif secteur in grille_sec.get("prioritaire", []):
        score += grille_sec.get("pts_prio", 25)
        reasons.append(f"Secteur prioritaire ({secteur})")
    elif secteur in grille_sec.get("secondaire", []):
        score += grille_sec.get("pts_sec", 15)
        reasons.append(f"Secteur secondaire ({secteur})")
    else:
        score += grille_sec.get("pts_hors", 5)
        reasons.append(f"Secteur hors cible ({secteur})")

    # ── Critère 2 — Effectif ──────────────────────────────────────────────
    if grille_eff.get("ideal_min", 50) <= effectif <= grille_eff.get("ideal_max", 250):
        score += grille_eff.get("pts_ideal", 25)
        reasons.append(f"Taille idéale ({effectif} salariés)")
    elif grille_eff.get("correct_min", 10) <= effectif <= grille_eff.get("correct_max", 49):
        score += grille_eff.get("pts_correct", 20)
        reasons.append(f"Taille correcte ({effectif} salariés)")
    elif grille_eff.get("grand_min", 251) <= effectif <= grille_eff.get("grand_max", 500):
        score += grille_eff.get("pts_grand", 15)
        reasons.append(f"Grande entreprise ({effectif} salariés)")
    else:
        score += grille_eff.get("pts_inadapte", 5)
        reasons.append(f"Taille inadaptée ({effectif} salariés)")

    # ── Critère 3 — Localisation ──────────────────────────────────────────
    if ville in grille_loc.get("optimale", []):
        score += grille_loc.get("pts_optimale", 20)
        reasons.append(f"Localisation optimale ({ville})")
    elif ville in grille_loc.get("partielle", []):
        score += grille_loc.get("pts_partielle", 15)
        reasons.append(f"Localisation partielle ({ville})")
    else:
        score += grille_loc.get("pts_hors", 5)
        reasons.append(f"Hors zone prioritaire ({ville})")

    # ── Critère 4 — Signal de croissance ──────────────────────────────────
    if signal and signal.lower() not in ["", "aucun", "nan"]:
        score += grille_sig.get("pts_signal", 25)
        reasons.append(f"Signal d'expansion : {signal}")
    else:
        score += grille_sig.get("pts_sans", 0)
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
