# Détecteur de phishing pour PME

![CI DevSecOps](https://github.com/gaddah-yousef/detecteur-phishing-pme/actions/workflows/ci.yml/badge.svg)

Prototype de détection et d'alerte précoce des URLs de phishing ciblant les PME.
Projet de stage PFA été 2026 — enrichi d'une chaîne DevSecOps complète
(tests, SAST, SCA, détection de secrets, CI GitHub Actions).

## Structure
- `jalon1/` — collecte d'URLs de phishing (PhishTank)
- `jalon2/` — modèle de détection (arbre de décision scikit-learn)
- `ROADMAP_DEVSECOPS.md` — la démarche DevSecOps appliquée