# Accidents de la route en France (BAAC) — Analyse Open Data

## Objectif
Analyser les accidents corporels de la circulation en France à partir des bases BAAC
afin d’identifier des patterns temporels et territoriaux (quand, où, qui est le plus touché) et produire des indicateurs utiles à la décision.

## Données
- Source : Bases de données annuelles des accidents corporels de la circulation (BAAC)
- Fichiers utilisés (par année) : caractéristiques, lieux, véhicules, usagers
- Niveau d’analyse :
  - Accident (caractéristiques + lieux)
  - Usager (gravité / profil) via jointures

## Méthodologie
1. Chargement robuste (séparateur/encodage)
2. Contrôle qualité (types, valeurs manquantes, doublons)
3. Jointures via l’identifiant d’accident (`Num_Acc`)
4. Feature engineering (date, heure, jour/semaine)
5. KPI + visualisations
6. Synthèse des insights & limites

## Résultats attendus (MVP)
- Accidents par heure / jour / mois
- Top départements (volume)
- Répartition de la gravité côté usagers
- Profils les plus exposés (catégorie d’usager, âge si disponible)

## Structure du repo
```text
accidents-france-baac/
├─ data/
│  ├─ raw/              # CSV bruts
│  └─ processed/        # datasets fusionnés
├─ notebooks/
│  ├─ 01_eda.ipynb      # exploration & contrôle qualité
│  └─ 02_insights.ipynb # analyses & recommandations
├─ src/                 # fonctions réutilisables (chargement/clean/kpi)
├─ outputs/
│  ├─ figures/
│  └─ report.md
├─ requirements.txt
└─ README.md
```

## How to run

### Prérequis
- Python 3.10+ (recommandé)
- Git (optionnel)

### Installation
```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```