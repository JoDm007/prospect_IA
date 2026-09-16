# Jeux de données de simulation — Yas Prospect Copilot

Ces fichiers contiennent des **données fictives de démonstration** : ils ne décrivent pas des données commerciales vérifiées, des coordonnées de personnes ou des décisions réelles de Yas Togo.

| Fichier | Usage |
| --- | --- |
| `entreprises.csv` | Jeu principal de 12 prospects, conforme au schéma SQLite défini dans le cahier des charges. |
| `messages_simules.csv` | Cinq emails de premier contact, chacun sous 100 mots. |
| `relances_j3_simulees.csv` | Deux relances J+3 prêtes pour la démonstration. |

## Cohérence avec le scoring

Les scores de `entreprises.csv` ont été recalculés strictement avec les quatre règles du cahier des charges : secteur, effectif, ville et signal de croissance. Un signal absent est une cellule vide (et non le texte `Aucun`), afin de valoir 0 point dans `scoring.py`.

Répartition obtenue : 7 prospects à haute priorité (75–100), 1 à priorité moyenne (60–74) et 4 disqualifiés. Les cas de démo demandés sont présents : **Ecobank Togo = 100**, **Togo Logistique SA = 90**, **Boulangerie de la Paix = 15**.
