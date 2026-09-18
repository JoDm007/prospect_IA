# scraper.py — Collecte de prospects depuis les annuaires togolais
# Sources : yellotogo.com, togo-annuaire.com
# Dépendances : requests, beautifulsoup4 (pip install beautifulsoup4)

import requests
from bs4 import BeautifulSoup
import re
import time
import random

# ── Headers pour éviter le blocage basique ────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TIMEOUT = 10  # secondes


# ── Utilitaires ───────────────────────────────────────────────────────────────

def _get(url: str) -> BeautifulSoup | None:
    """Télécharge une page et retourne le soup, ou None en cas d'erreur."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.exceptions.Timeout:
        print(f"[SCRAPER] Timeout : {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[SCRAPER] Erreur HTTP {e.response.status_code} : {url}")
        return None
    except Exception as e:
        print(f"[SCRAPER] Erreur réseau : {e} — {url}")
        return None


def _clean(text: str) -> str:
    """Nettoie un texte : supprime espaces multiples et caractères parasites."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def _deviner_secteur(nom: str, description: str = "") -> str:
    """Déduit le secteur à partir du nom ou de la description de l'entreprise."""
    texte = (nom + " " + description).lower()
    mapping = {
        "Banque":          ["banque", "bank", "crédit", "microfinance", "épargne", "caisse"],
        "Assurance":       ["assurance", "assur", "mutuelle", "prévoyance"],
        "Logistique":      ["logistique", "transport", "livraison", "fret", "transit", "cargo"],
        "Informatique":    ["informatique", "digital", "tech", "software", "web", "it ", "saas", "startup"],
        "Éducation":       ["école", "université", "formation", "éducation", "lycée", "college", "académie"],
        "Commerce":        ["commerce", "boutique", "supermarché", "distribution", "import", "export", "négoce"],
        "Industrie":       ["industrie", "fabrique", "manufacture", "production", "usine", "btp", "construction"],
        "Agroalimentaire": ["agro", "alimentaire", "agriculture", "ferme", "élevage", "boulanger", "restaur"],
        "Conseil":         ["conseil", "consulting", "cabinet", "audit", "expertise", "juridique", "rh"],
        "Santé":           ["clinique", "hôpital", "santé", "médecin", "pharmacie", "laboratoire"],
        "Télécom":         ["télécom", "telecom", "réseau", "mobile", "internet", "fai"],
        "Immobilier":      ["immobilier", "promoteur", "agence immob", "construction"],
        "Energie":         ["énergie", "solaire", "électricité", "pétrole", "gaz"],
    }
    for secteur, mots in mapping.items():
        if any(m in texte for m in mots):
            return secteur
    return "Autre"


def _deviner_effectif(texte: str) -> int:
    """Extrait une estimation d'effectif depuis un texte libre."""
    if not texte:
        return 10
    # Cherche un nombre suivi d'un mot lié aux employés
    match = re.search(r"(\d+)\s*(employ|salarié|staff|person|agent|collabor)", texte.lower())
    if match:
        n = int(match.group(1))
        return min(n, 500)
    return 10


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 1 — yellotogo.com
# ══════════════════════════════════════════════════════════════════════════════

YELLOTOGO_BASE = "https://www.yellotogo.com"

def scraper_yellotogo(secteur: str = "", ville: str = "Lomé", max_pages: int = 3) -> list[dict]:
    """
    Scrape les entreprises depuis yellotogo.com.

    Args:
        secteur   : mot-clé de recherche (ex: "banque", "logistique")
        ville     : ville de recherche
        max_pages : nombre de pages à parcourir (chaque page ≈ 10 résultats)

    Returns:
        Liste de dicts avec les champs attendus par le pipeline
    """
    resultats = []
    query = f"{secteur} {ville}".strip().replace(" ", "+")
    
    for page in range(1, max_pages + 1):
        url = f"{YELLOTOGO_BASE}/search?q={query}&page={page}"
        print(f"[yellotogo] Scraping page {page} : {url}")
        soup = _get(url)
        if not soup:
            break

        # Cartes d'entreprises (structure observée sur le site)
        cards = (
            soup.find_all("div", class_=re.compile(r"listing|company|result|card", re.I))
            or soup.find_all("li", class_=re.compile(r"listing|company|result", re.I))
            or soup.find_all("article")
        )

        if not cards:
            # Fallback : chercher les liens avec texte d'entreprise
            liens = soup.find_all("a", href=re.compile(r"/entreprise|/company|/listing"))
            for lien in liens[:10]:
                nom = _clean(lien.get_text())
                if nom and len(nom) > 3:
                    resultats.append(_construire_prospect(
                        nom=nom, ville=ville, secteur_hint=secteur
                    ))
            break

        for card in cards[:10]:
            nom_tag = (
                card.find(["h2", "h3", "h4", "strong"])
                or card.find(class_=re.compile(r"name|title|nom", re.I))
            )
            nom = _clean(nom_tag.get_text()) if nom_tag else ""
            if not nom or len(nom) < 3:
                continue

            # Description / activité
            desc_tag = card.find(class_=re.compile(r"desc|activity|categor|sector", re.I))
            desc = _clean(desc_tag.get_text()) if desc_tag else ""

            # Ville
            ville_tag = card.find(class_=re.compile(r"city|location|address|ville", re.I))
            ville_trouvee = _clean(ville_tag.get_text()) if ville_tag else ville

            # Signal potentiel : chercher dans la description
            signal = ""
            if desc:
                mots_signal = ["recrut", "expansion", "nouveau", "ouvert", "lancé", "développ", "levée"]
                if any(m in desc.lower() for m in mots_signal):
                    signal = desc[:120]

            resultats.append(_construire_prospect(
                nom=nom,
                ville=ville_trouvee or ville,
                secteur_hint=secteur or desc,
                signal=signal,
            ))

        # Pause polie entre pages
        time.sleep(random.uniform(1.0, 2.0))

    print(f"[yellotogo] {len(resultats)} entreprise(s) collectée(s)")
    return resultats


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 2 — togo-annuaire.com  (annuaire des entreprises togolaises)
# ══════════════════════════════════════════════════════════════════════════════

TOGOAN_BASE = "https://www.togo-annuaire.com"

def scraper_togo_annuaire(secteur: str = "", ville: str = "Lomé", max_pages: int = 3) -> list[dict]:
    """
    Scrape les entreprises depuis togo-annuaire.com.

    Args:
        secteur   : catégorie ou mot-clé (ex: "banques", "assurances")
        ville     : ville ciblée
        max_pages : nombre de pages à parcourir

    Returns:
        Liste de dicts de prospects
    """
    resultats = []
    query = f"{secteur} {ville}".strip().replace(" ", "-").lower()

    for page in range(1, max_pages + 1):
        url = f"{TOGOAN_BASE}/recherche/{query}/page/{page}" if page > 1 else f"{TOGOAN_BASE}/recherche/{query}"
        print(f"[togo-annuaire] Scraping page {page} : {url}")
        soup = _get(url)
        if not soup:
            break

        # Cherche les blocs d'entreprises
        cards = (
            soup.find_all("div", class_=re.compile(r"company|listing|entreprise|result|item", re.I))
            or soup.find_all("li", class_=re.compile(r"company|listing|entreprise|result", re.I))
            or soup.find_all("article")
        )

        if not cards:
            # Fallback liens
            liens = soup.find_all("a", href=re.compile(r"/entreprise|/societe|/company"))
            for lien in liens[:10]:
                nom = _clean(lien.get_text())
                if nom and len(nom) > 3:
                    resultats.append(_construire_prospect(nom=nom, ville=ville, secteur_hint=secteur))
            break

        for card in cards[:10]:
            nom_tag = (
                card.find(["h2", "h3", "h4", "strong", "b"])
                or card.find(class_=re.compile(r"name|title|nom|raison", re.I))
            )
            nom = _clean(nom_tag.get_text()) if nom_tag else ""
            if not nom or len(nom) < 3:
                continue

            # Activité / description
            desc_tag = card.find(class_=re.compile(r"activit|desc|sector|categor", re.I))
            desc = _clean(desc_tag.get_text()) if desc_tag else ""

            # Adresse / ville
            addr_tag = card.find(class_=re.compile(r"address|adresse|city|ville|location", re.I))
            ville_trouvee = _clean(addr_tag.get_text()) if addr_tag else ville
            # Garde seulement le premier mot de la ville
            if "," in ville_trouvee:
                ville_trouvee = ville_trouvee.split(",")[0].strip()

            # Téléphone (indicateur de présence digitale)
            tel_tag = card.find(class_=re.compile(r"phone|tel|contact", re.I))
            a_tel   = bool(tel_tag and tel_tag.get_text().strip())

            resultats.append(_construire_prospect(
                nom=nom,
                ville=ville_trouvee or ville,
                secteur_hint=secteur or desc,
                signal="",
                site_web=a_tel,
            ))

        time.sleep(random.uniform(1.0, 2.0))

    print(f"[togo-annuaire] {len(resultats)} entreprise(s) collectée(s)")
    return resultats


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE 3 — Enrichissement depuis le site web de l'entreprise
# ══════════════════════════════════════════════════════════════════════════════

def enrichir_depuis_site(entreprise: dict) -> dict:
    """
    Visite le site web d'un prospect pour détecter des signaux de croissance.

    Signaux recherchés : recrutement, expansion, nouveau produit, levée de fonds.

    Args:
        entreprise : dict avec au minimum 'nom' et optionnellement 'site_web_url'

    Returns:
        Le dict enrichi avec 'signal_croissance' si détecté
    """
    url = entreprise.get("site_web_url", "")
    if not url:
        return entreprise

    if not url.startswith("http"):
        url = "https://" + url

    print(f"[enrichir] Visite de {url}")
    soup = _get(url)
    if not soup:
        return entreprise

    texte = soup.get_text(separator=" ", strip=True).lower()

    SIGNAUX = {
        "Recrutement en cours":        ["on recrute", "nous recrutons", "offre d'emploi", "job", "carrière", "rejoindre notre équipe"],
        "Expansion géographique":      ["nouveau bureau", "nouvelle agence", "ouverture", "expansion", "nous étendons"],
        "Lancement produit/service":   ["nouveau service", "nouveau produit", "lancement", "bêta", "disponible dès maintenant"],
        "Levée de fonds / partenariat":["levée de fonds", "investissement", "partenariat stratégique", "accord", "financement"],
        "Digitalisation":              ["digitalisation", "transformation numérique", "plateforme", "application", "api"],
    }

    for label, mots in SIGNAUX.items():
        if any(m in texte for m in mots):
            entreprise["signal_croissance"] = label
            print(f"[enrichir] Signal détecté pour {entreprise.get('nom')} : {label}")
            break

    entreprise["site_web"] = True
    return entreprise


# ══════════════════════════════════════════════════════════════════════════════
# Constructeur de prospect normalisé
# ══════════════════════════════════════════════════════════════════════════════

def _construire_prospect(
    nom: str,
    ville: str = "Lomé",
    secteur_hint: str = "",
    signal: str = "",
    effectif: int = 0,
    site_web: bool = False,
) -> dict:
    """
    Construit un dict prospect normalisé prêt pour le pipeline de scoring.
    Les champs correspondent exactement au schéma de database.py.
    """
    return {
        "nom":               nom,
        "secteur":           _deviner_secteur(nom, secteur_hint),
        "localisation":      _normaliser_ville(ville),
        "effectif":          effectif or 15,  # valeur par défaut si inconnue
        "signal_croissance": signal,
        "site_web":          site_web,
        "paiement_en_ligne": False,
        "score":             0,   # sera calculé par scoring.py
        "score_reasons":     "",
        "statut":            "Nouveau",
        "date_contact":      None,
        "message_genere":    None,
        "source":            "scraping",
    }


def _normaliser_ville(ville: str) -> str:
    """Normalise le nom de ville pour correspondre aux villes connues du scoring."""
    ville_lower = ville.lower().strip()
    mapping = {
        "lomé": "Lomé", "lome": "Lomé",
        "kara": "Kara",
        "tsévié": "Tsevié", "tsevie": "Tsevié",
        "kpalimé": "Kpalimé", "kpalime": "Kpalimé",
        "sokodé": "Sokodé", "sokode": "Sokodé",
        "atakpamé": "Atakpamé", "atakpame": "Atakpamé",
        "dapaong": "Dapaong",
    }
    for k, v in mapping.items():
        if k in ville_lower:
            return v
    return ville.strip() or "Lomé"


# ══════════════════════════════════════════════════════════════════════════════
# Fonction principale : scraping multi-sources + scoring
# ══════════════════════════════════════════════════════════════════════════════

def scraper_prospects(
    secteur: str = "",
    ville: str = "Lomé",
    sources: list[str] | None = None,
    max_pages: int = 2,
    callback=None,
) -> list[dict]:
    """
    Lance le scraping sur les sources sélectionnées, applique le scoring ICP,
    déduplique par nom, et retourne les prospects prêts à être importés.

    Args:
        secteur   : secteur/mot-clé de recherche
        ville     : ville cible
        sources   : liste parmi ["yellotogo", "togo_annuaire"]
                    (None = toutes les sources)
        max_pages : pages à scraper par source
        callback  : fonction(message: str) appelée pour mise à jour UI (Streamlit)

    Returns:
        Liste de dicts prospects avec score calculé, triée par score décroissant
    """
    from scoring import score_prospect

    if sources is None:
        sources = ["yellotogo", "togo_annuaire"]

    tous = []

    if "yellotogo" in sources:
        if callback:
            callback("🔍 Scraping yellotogo.com…")
        try:
            r = scraper_yellotogo(secteur=secteur, ville=ville, max_pages=max_pages)
            tous.extend(r)
            if callback:
                callback(f"✅ yellotogo.com : {len(r)} entreprise(s) trouvée(s)")
        except Exception as e:
            print(f"[SCRAPER] yellotogo erreur : {e}")
            if callback:
                callback(f"⚠️ yellotogo.com indisponible ({e})")

    if "togo_annuaire" in sources:
        if callback:
            callback("🔍 Scraping togo-annuaire.com…")
        try:
            r = scraper_togo_annuaire(secteur=secteur, ville=ville, max_pages=max_pages)
            tous.extend(r)
            if callback:
                callback(f"✅ togo-annuaire.com : {len(r)} entreprise(s) trouvée(s)")
        except Exception as e:
            print(f"[SCRAPER] togo-annuaire erreur : {e}")
            if callback:
                callback(f"⚠️ togo-annuaire.com indisponible ({e})")

    # Déduplication par nom (insensible à la casse)
    vus = set()
    uniques = []
    for p in tous:
        cle = p["nom"].lower().strip()
        if cle not in vus and len(cle) > 2:
            vus.add(cle)
            uniques.append(p)

    # Calcul du score ICP pour chaque prospect
    for p in uniques:
        try:
            score, reasons, _ = score_prospect(p)
            p["score"]        = score
            p["score_reasons"] = reasons
            if score >= 75:
                p["statut"] = "Scoré"
        except Exception as e:
            print(f"[SCRAPER] Score erreur pour {p.get('nom')} : {e}")

    # Tri par score décroissant
    uniques.sort(key=lambda x: x.get("score", 0), reverse=True)

    if callback:
        callback(f"🎯 {len(uniques)} prospect(s) unique(s) scoré(s) — prêt(s) pour import")

    print(f"[SCRAPER] Total final : {len(uniques)} prospects uniques")
    return uniques


# ══════════════════════════════════════════════════════════════════════════════
# CLI de test
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  TEST scraper.py — Annuaires togolais")
    print("=" * 60)
    resultats = scraper_prospects(secteur="banque", ville="Lomé", max_pages=1)
    print(f"\n{len(resultats)} prospect(s) collecté(s) :")
    for p in resultats[:5]:
        print(f"  [{p['score']:3d}] {p['nom']:<30} | {p['secteur']:<15} | {p['localisation']}")
    print("=" * 60)
