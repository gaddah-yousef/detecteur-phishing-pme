# Détecteur de phishing pour PME

[![CI DevSecOps](https://github.com/gaddah-yousef/detecteur-phishing-pme/actions/workflows/ci.yml/badge.svg)](https://github.com/gaddah-yousef/detecteur-phishing-pme/actions/workflows/ci.yml)

**Projet pédagogique de Cyber Threat Intelligence, détection d'URLs suspectes et DevSecOps.** L'objectif est d'explorer une chaîne progressive allant de l'acquisition d'indicateurs de phishing à leur analyse et à leur visualisation pour des PME.

> **Statut : prototype par jalons.** La collecte, l'extraction de caractéristiques, les tests associés et un tableau de bord de consultation des signalements sont présents. L'entraînement complet d'un modèle, sa validation sur un jeu de données étiqueté et son intégration au tableau de bord ne sont **pas démontrés par l'état actuel du dépôt**. Ne pas présenter ce projet comme un détecteur de phishing prêt pour la production.

## 1. Problématique et objectifs

Les PME ont besoin de moyens accessibles pour examiner les indicateurs de phishing et comprendre les signaux de risque d'une URL. Ce projet explore trois axes complémentaires :

- **Threat Intelligence :** collecte d'URLs signalées et consultation de leur contexte.
- **Détection :** extraction de caractéristiques lexicales d'URL en vue d'un modèle de classification.
- **Industrialisation :** qualité du code, tests et contrôles de sécurité dans GitHub Actions.

Le système aide à étudier des signalements ; il ne garantit ni qu'une URL non signalée soit sûre ni qu'un signalement soit encore actif.

## 2. Architecture et périmètre

```text
Flux public PhishTank (CSV)
         |
         v
jalon1/telecharger_urls.py
  téléchargement + nettoyage + export CSV local
         |
         v
jalon1/data/urls_phishing_*.csv
         |
         +------------------> jalon3/app.py
         |                    Streamlit : volumes, marques, derniers signalements
         |
         +--> jalon2/entrainer_modele.py
              extraction de 13 caractéristiques d'URL
                       |
                       v
              [à compléter : entraînement et évaluation]
                       |
                       v
              models/phishing_detector.joblib (non fourni)
                       |
                       v
              jalon2/tester_modele.py
              prédiction sur un modèle préalablement entraîné
```

### Réalisé et à compléter

| Composant | État observable dans le dépôt |
|---|---|
| Collecte de signalements | Script Python utilisant `requests` et `pandas` |
| Export de données | CSV horodatés dans `jalon1/data/` |
| Extraction de caractéristiques | 13 variables lexicales et structurelles d'URL |
| Interface Streamlit | Affichage du CSV de collecte, statistiques et top des marques |
| Prédiction par modèle | Script de chargement disponible ; artefact de modèle non fourni |
| Entraînement/évaluation ML | Documentation pédagogique ; pipeline d'entraînement complet à finaliser |
| DevSecOps | GitHub Actions : Ruff, pytest, Bandit, pip-audit et Gitleaks |

## 3. Structure du dépôt

```text
.
├── .github/workflows/ci.yml      # Intégration continue et contrôles de sécurité
├── jalon1/
│   ├── telecharger_urls.py       # Collecte et export PhishTank
│   ├── note_phishing.md          # Notes sur la menace
│   └── requirements.txt
├── jalon2/
│   ├── entrainer_modele.py       # Extraction de caractéristiques
│   ├── tester_modele.py          # Chargement d'un modèle sauvegardé
│   ├── explorer_dataset.py
│   ├── GUIDE_JALON2.md           # Démarche ML détaillée
│   ├── resultats_jalon2.md
│   └── tests/
├── jalon3/
│   └── app.py                    # Tableau de bord Streamlit
├── ROADMAP_DEVSECOPS.md
├── requirements.txt
└── requirements-dev.txt
```

Les données collectées et les modèles entraînés localement ne doivent pas être confondus avec des résultats versionnés dans le dépôt.

## 4. Installation et démonstration

### Prérequis

- Python 3 et `pip` ;
- connexion réseau pour récupérer les signalements ;
- accès à un environnement de laboratoire autorisé.

```bash
git clone https://github.com/gaddah-yousef/detecteur-phishing-pme.git
cd detecteur-phishing-pme
python -m venv .venv
# Linux/macOS : source .venv/bin/activate
# Windows PowerShell : .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
```

**Étape A — Collecter les signalements**

```bash
python jalon1/telecharger_urls.py
```

Le script interroge un flux CSV PhishTank, résume les indicateurs reçus et génère un fichier local sous `jalon1/data/`. **Attention : l'URL actuellement codée dans ce script utilise HTTP et non HTTPS.** Vérifier la disponibilité et la sécurité de la source avant de l'intégrer à un processus réel.

**Étape B — Explorer les caractéristiques d'une URL**

```bash
python jalon2/entrainer_modele.py
```

À ce stade, le fichier exécute une **démonstration d'extraction de caractéristiques** : longueur, sous-domaines approximatifs, chiffres, présence d'une IP, marqueurs suspects, encodage, HTTPS, etc. Il **n'entraîne pas** un modèle lors de cette exécution.

**Étape C — Visualiser les signalements**

```bash
streamlit run jalon3/app.py
```

Le tableau de bord nécessite un CSV généré à l'étape A. Il affiche les signalements et statistiques de source ; il n'affiche pas encore une prédiction calculée par un modèle entraîné.

### Tests et contrôles locaux

```bash
python -m pytest -v
ruff check .
bandit -r jalon1 jalon2 -x jalon2/tests
pip-audit
```

La CI ajoute également un contrôle Gitleaks. Les résultats dépendent de l'environnement et de la version des dépendances ; ce README ne prétend pas que tous les contrôles réussissent sans exécution.

## 5. Méthodologie de détection

Les caractéristiques d'URL calculées comprennent notamment :

| Famille | Exemples | Limite |
|---|---|---|
| Structure | longueur d'URL/domaine, points, sous-domaines | un domaine long n'est pas nécessairement malveillant |
| Contenu | mots tels que `login`, `verify`, `account` | des sites légitimes utilisent aussi ces mots |
| Syntaxe | `@`, adresse IP, encodage `%XX`, double slash dans le chemin | indicateurs non suffisants seuls |
| Transport | présence du schéma `https` | HTTPS ne garantit pas qu'un site soit fiable |

Pour aller vers une classification fiable, il faudra documenter : provenance et licence du dataset, déduplication, partage entraînement/test sans fuite, déséquilibre des classes, précision, rappel, F1, matrice de confusion et seuil de décision.

## 6. Sécurité, limites et bonnes pratiques

- **Ne pas ouvrir automatiquement** les URLs de phishing collectées dans un navigateur personnel.
- Ne pas scanner ni solliciter des domaines tiers sans autorisation.
- Préférer l'analyse **statique** des chaînes d'URL dans un laboratoire isolé.
- Aucune prédiction ne doit être présentée comme un verdict définitif sans validation.
- Le script `tester_modele.py` nécessite un fichier `models/phishing_detector.joblib` compatible qui n'est pas présent dans l'arborescence actuelle.
- Ne pas charger d'artefacts `joblib` non fiables : leur désérialisation peut exécuter du code.

## 7. Feuille de route

1. Finaliser un pipeline d'entraînement reproductible et sauvegarder les métriques de validation.
2. Connecter les prédictions du modèle au tableau de bord Streamlit.
3. Ajouter des tests de bout en bout sur données synthétiques.
4. Documenter la gestion des faux positifs et la mise à jour des indicateurs.
5. Ajouter des jeux de démonstration sans URLs dangereuses pour une démo hors ligne.

## 8. Compétences mises en pratique

**CTI / OSINT défensif · Python · Pandas · Feature engineering · Scikit-learn · Streamlit · Tests · SAST · SCA · Secret scanning · GitHub Actions.**

Pour approfondir, lire [le guide du jalon 2](jalon2/GUIDE_JALON2.md) et [la roadmap DevSecOps](ROADMAP_DEVSECOPS.md).

**Auteur / portfolio :** [Yousef Gaddah](https://github.com/gaddah-yousef) — projet de formation et expérimentation en cybersécurité.
