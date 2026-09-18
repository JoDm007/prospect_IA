# database.py — Gestion SQLite pour CibleNet
# Fournit toutes les opérations CRUD sur la table entreprises

import sqlite3
import csv
import os
from datetime import date
from scoring import score_prospect

# ── Chemins ───────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "data", "prospects.db")
CSV_PATH  = os.path.join(BASE_DIR, "data", "entreprises.csv")

# ── Connexion ─────────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """Retourne une connexion SQLite avec row_factory pour accès par nom de colonne."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Initialisation ────────────────────────────────────────────────────────────

def init_db() -> None:
    """Crée la table entreprises si elle n'existe pas encore."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entreprises (
            id                INTEGER PRIMARY KEY,
            nom               TEXT    NOT NULL,
            secteur           TEXT,
            localisation      TEXT,
            effectif          INTEGER,
            signal_croissance TEXT,
            site_web          BOOLEAN DEFAULT 0,
            paiement_en_ligne BOOLEAN DEFAULT 0,
            score             INTEGER DEFAULT 0,
            score_reasons     TEXT,
            statut            TEXT    DEFAULT 'Nouveau',
            date_contact      DATE,
            message_genere    TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Base initialisée : {DB_PATH}")


# ── Import CSV ────────────────────────────────────────────────────────────────

def import_from_csv(csv_path: str = CSV_PATH, recalculate_scores: bool = False) -> int:
    """
    Importe les entreprises depuis le CSV dans SQLite.
    Ignore les entrées dont l'id existe déjà (INSERT OR IGNORE).

    Args:
        csv_path         : chemin vers entreprises.csv
        recalculate_scores: si True, recalcule les scores via scoring.py

    Returns:
        Nombre de lignes insérées.
    """
    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Recalcul optionnel du score
            if recalculate_scores:
                score, reasons, _ = score_prospect(row)
                row["score"] = score
                row["score_reasons"] = reasons

            # Normalisation booléens
            site_web          = str(row.get("site_web", "false")).lower() == "true"
            paiement_en_ligne = str(row.get("paiement_en_ligne", "false")).lower() == "true"

            cursor.execute("""
                INSERT OR IGNORE INTO entreprises
                    (id, nom, secteur, localisation, effectif, signal_croissance,
                     site_web, paiement_en_ligne, score, score_reasons,
                     statut, date_contact, message_genere)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["id"]),
                row["nom"],
                row["secteur"],
                row["localisation"],
                int(row["effectif"]),
                row.get("signal_croissance", ""),
                site_web,
                paiement_en_ligne,
                int(row.get("score", 0)),
                row.get("score_reasons", ""),
                row.get("statut", "Nouveau"),
                row.get("date_contact") or None,
                row.get("message_genere") or None,
            ))
            if cursor.rowcount:
                inserted += 1

    conn.commit()
    conn.close()
    print(f"[DB] Import CSV : {inserted} entreprise(s) insérée(s).")
    return inserted


# ── Lecture ───────────────────────────────────────────────────────────────────

def get_all_entreprises() -> list[dict]:
    """Retourne toutes les entreprises triées par score décroissant."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM entreprises ORDER BY score DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_entreprise_by_id(entreprise_id: int) -> dict | None:
    """Retourne une entreprise par son id, ou None si introuvable."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM entreprises WHERE id = ?", (entreprise_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def search_entreprises(secteur: str = "", localisation: str = "", effectif_min: int = 0, effectif_max: int = 9999) -> list[dict]:
    """
    Recherche des entreprises avec filtres optionnels.

    Args:
        secteur      : filtre exact sur secteur (vide = tous)
        localisation : filtre exact sur localisation (vide = tous)
        effectif_min : borne basse de l'effectif
        effectif_max : borne haute de l'effectif

    Returns:
        Liste de dicts, triée par score décroissant.
    """
    query  = "SELECT * FROM entreprises WHERE 1=1"
    params = []

    if secteur:
        query += " AND secteur = ?"
        params.append(secteur)
    if localisation:
        query += " AND localisation = ?"
        params.append(localisation)

    query += " AND effectif BETWEEN ? AND ?"
    params += [effectif_min, effectif_max]
    query += " ORDER BY score DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pipeline() -> dict[str, list[dict]]:
    """
    Retourne les entreprises groupées par statut pour la vue kanban.

    Returns:
        Dict { statut: [entreprise, ...] }
    """
    statuts = ["Nouveau", "Scoré", "Contacté", "Relancé", "Converti", "Non intéressé", "À relancer plus tard"]
    conn = get_connection()
    pipeline = {}
    for s in statuts:
        rows = conn.execute(
            "SELECT * FROM entreprises WHERE statut = ? ORDER BY score DESC", (s,)
        ).fetchall()
        pipeline[s] = [dict(r) for r in rows]
    conn.close()
    return pipeline


def get_converted_entreprises() -> list[dict]:
    """Retourne les prospects convertis pour l'onglet Handoff."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM entreprises WHERE statut = 'Converti' ORDER BY score DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Mise à jour ───────────────────────────────────────────────────────────────

def update_statut(entreprise_id: int, nouveau_statut: str) -> bool:
    """
    Met à jour le statut d'une entreprise.
    Si le statut est 'Contacté', met aussi à jour date_contact avec aujourd'hui.

    Returns:
        True si la mise à jour a réussi.
    """
    conn = get_connection()
    if nouveau_statut == "Contacté":
        conn.execute(
            "UPDATE entreprises SET statut = ?, date_contact = ? WHERE id = ?",
            (nouveau_statut, date.today().isoformat(), entreprise_id)
        )
    else:
        conn.execute(
            "UPDATE entreprises SET statut = ? WHERE id = ?",
            (nouveau_statut, entreprise_id)
        )
    affected = conn.total_changes
    conn.commit()
    conn.close()
    return affected > 0


def save_message(entreprise_id: int, message: str) -> bool:
    """
    Sauvegarde le message généré par le LLM et passe le statut à 'Contacté'.

    Returns:
        True si la mise à jour a réussi.
    """
    conn = get_connection()
    conn.execute(
        """UPDATE entreprises
           SET message_genere = ?, statut = 'Contacté', date_contact = ?
           WHERE id = ?""",
        (message, date.today().isoformat(), entreprise_id)
    )
    affected = conn.total_changes
    conn.commit()
    conn.close()
    return affected > 0


def update_score(entreprise_id: int, score: int, score_reasons: str) -> bool:
    """Met à jour le score et les raisons d'une entreprise."""
    conn = get_connection()
    conn.execute(
        "UPDATE entreprises SET score = ?, score_reasons = ?, statut = 'Scoré' WHERE id = ?",
        (score, score_reasons, entreprise_id)
    )
    affected = conn.total_changes
    conn.commit()
    conn.close()
    return affected > 0


# ── Statistiques ──────────────────────────────────────────────────────────────

def get_stats() -> dict:
    """Retourne les statistiques globales du pipeline."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM entreprises").fetchone()[0]
    convertis = conn.execute("SELECT COUNT(*) FROM entreprises WHERE statut = 'Converti'").fetchone()[0]
    haute_priorite = conn.execute("SELECT COUNT(*) FROM entreprises WHERE score >= 75").fetchone()[0]
    par_statut = {}
    rows = conn.execute("SELECT statut, COUNT(*) as n FROM entreprises GROUP BY statut").fetchall()
    for r in rows:
        par_statut[r["statut"]] = r["n"]
    conn.close()

    taux_conversion = round((convertis / total * 100), 1) if total > 0 else 0
    return {
        "total": total,
        "convertis": convertis,
        "haute_priorite": haute_priorite,
        "taux_conversion": taux_conversion,
        "par_statut": par_statut,
    }


# ── Bootstrap (init + import au premier lancement) ───────────────────────────

def bootstrap() -> None:
    """Initialise la base et importe le CSV si la table est vide."""
    init_db()
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM entreprises").fetchone()[0]
    conn.close()
    if count == 0:
        print("[DB] Table vide — import du CSV...")
        import_from_csv()
    else:
        print(f"[DB] Base déjà peuplée ({count} entreprises).")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bootstrap()
    print("\n── Toutes les entreprises (score décroissant) ──")
    for e in get_all_entreprises():
        print(f"  [{e['score']:3d}] {e['nom']:<30} | {e['statut']:<22} | {e['localisation']}")

    print("\n── Statistiques pipeline ──")
    stats = get_stats()
    print(f"  Total       : {stats['total']}")
    print(f"  Convertis   : {stats['convertis']} ({stats['taux_conversion']}%)")
    print(f"  Haute prior.: {stats['haute_priorite']}")
    print(f"  Par statut  :")
    for s, n in stats["par_statut"].items():
        print(f"    {s:<25} : {n}")
