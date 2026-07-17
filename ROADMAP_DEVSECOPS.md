# Roadmap DevSecOps — Détecteur de phishing pour PME

*Couche DevSecOps posée sur le projet de stage PFA. Objectif double : livrer un
projet plus solide **et** apprendre le DevSecOps sur un cas concret.*

---

## 1. C'est quoi le DevSecOps, en une phrase ?

C'est le fait d'**intégrer la sécurité à chaque étape** du cycle de vie d'un
logiciel (au lieu de la traiter à la fin), de façon **automatisée**. On parle de
*« shift left »* : déplacer la sécurité le plus tôt possible, dès le code.

Le cycle DevSecOps est souvent dessiné comme une boucle infinie :

```
   PLAN → CODE → BUILD → TEST → RELEASE → DEPLOY → OPERATE → MONITOR
     └──────────────── la sécurité à CHAQUE étape ─────────────────┘
```

**Pourquoi c'est pertinent ici ?** Notre app :
- manipule un **mot de passe e-mail** (module `smtplib`) → gestion des secrets ;
- traite des **URLs non fiables** en entrée → validation des entrées ;
- **est** un outil de sécurité → cohérent de pratiquer un développement sécurisé.

> ⚠️ **Proportion.** Ce projet est un stage d'apprentissage. On NE fait PAS de
> Kubernetes, Terraform, ni stack d'observabilité complète. On vise les **Phases
> 0 à 3** (déjà très riches et réalistes). Les Phases 4–5 sont des bonus.

---

## 2. Les phases (adaptées au projet)

### Phase 0 — Fondations · *Plan + Code*  ⬅️ à faire en premier
**Objectif :** mettre le projet dans un état professionnel et sûr.

| Action | Outil (gratuit) | Ce que tu apprends |
|---|---|---|
| Versionner le projet | **Git** + **GitHub** | Contrôle de version, commits, branches |
| Ignorer les fichiers sensibles/lourds | `.gitignore` | Ne jamais committer `.venv/`, `data/`, `models/`, secrets |
| Sortir le mot de passe e-mail du code | **python-dotenv** + fichier `.env` | Gestion des secrets, `.env` jamais committé |
| Nettoyer (2 `.venv` en double, `requirements.txt` en UTF-16) | — | Hygiène de projet |
| Documenter | `README.md` | Rendre le projet compréhensible |

**Livrable :** dépôt GitHub propre, secrets hors du code, README.

---

### Phase 1 — Qualité & Tests · *Test*
**Objectif :** garantir que le code marche et reste lisible.

| Action | Outil | Ce que tu apprends |
|---|---|---|
| Tests automatiques (ex. `extraire_caracteristiques`) | **pytest** | Tests unitaires |
| Mesurer la couverture | **pytest-cov** | Notion de code coverage |
| Linter + formater le code | **ruff** | Qualité et style de code |
| Vérifier les types (le code a déjà des type hints) | **mypy** *(optionnel)* | Typage statique |

**Livrable :** dossier `tests/` qui passe au vert.

---

### Phase 2 — Sécurité intégrée · *Sec* 🔒 (le cœur du DevSecOps)
**Objectif :** détecter automatiquement les failles. Les 3 piliers de base :

| Type | Outil | Rôle |
|---|---|---|
| **SAST** (analyse statique du code) | **Bandit** | Repère les patterns dangereux en Python |
| **SCA** (analyse des dépendances) | **pip-audit** | Trouve les vulnérabilités connues (CVE) dans pandas, sklearn… |
| **Secrets scanning** | **gitleaks** | Détecte tout mot de passe/clé committé par erreur |

**Livrable :** rapports de scan + corrections des alertes trouvées.

---

### Phase 3 — Automatisation CI/CD · *Build + Release*
**Objectif :** exécuter tout ça **automatiquement à chaque `git push`**.

- Outil : **GitHub Actions** (gratuit pour un dépôt public).
- Un fichier `.github/workflows/ci.yml` qui, à chaque push, enchaîne :
  `ruff` (lint) → `pytest` (tests) → `bandit` (SAST) → `pip-audit` (SCA) → `gitleaks` (secrets).
- Bonus : activer **Dependabot** (natif GitHub) pour les mises à jour de sécurité.

**C'est ici que le DevSecOps prend tout son sens** : la sécurité devient une
barrière automatique, pas une étape oubliée. **Livrable :** pipeline vert + badge dans le README.

---

### Phase 4 — Conteneurisation · *Deploy* (bonus)
**Objectif :** empaqueter l'app pour qu'elle tourne partout à l'identique.

| Action | Outil | Ce que tu apprends |
|---|---|---|
| Créer une image de l'app Streamlit | **Docker** (`Dockerfile`) | Conteneurs |
| Scanner l'image | **Trivy** | Vulnérabilités des images Docker |

---

### Phase 5 — Déploiement & Supervision · *Operate + Monitor* (bonus)
**Objectif :** mettre l'app en ligne et la surveiller.

- Déploiement gratuit : **Streamlit Community Cloud**.
- Journalisation (logs) des détections.
- **DAST** *(optionnel)* : **OWASP ZAP** pour tester l'app en fonctionnement.

---

## 3. Correspondance avec le cycle DevSecOps

| Étape du cycle | Dans ce projet |
|---|---|
| Plan | Cadrage, cette roadmap, issues GitHub |
| Code | Python + `.env` pour les secrets + pre-commit |
| Build | Docker (Phase 4) |
| Test | pytest + ruff (Phase 1) |
| **Sec** *(transversal)* | Bandit + pip-audit + gitleaks + Trivy |
| Release | GitHub Actions (Phase 3) |
| Deploy | Streamlit Cloud (Phase 5) |
| Operate/Monitor | Logs, ZAP (Phase 5) |

---

## 4. Ordre conseillé (réaliste pour un stage)

1. **Phase 0** — Git + secrets + nettoyage *(indispensable, base de tout)*
2. **Phase 1** — Tests + lint
3. **Phase 2** — Les 3 scanners de sécurité
4. **Phase 3** — Pipeline GitHub Actions *(le moment « waouh » du DevSecOps)*
5. *(bonus)* **Phase 4–5** — Docker + déploiement si le temps le permet

> 💡 À valider avec l'encadrant : cette couche va **au-delà** de la fiche de
> cadrage. C'est un excellent plus, mais préviens Pr. Bentaleb pour que ce soit
> reconnu dans l'évaluation, et garde l'application elle-même simple (Jalon 3).

---

## 5. État actuel du projet (point de départ)

- ✅ Jalon 1 (téléchargement URLs) et Jalon 2 (modèle) fonctionnels.
- ❌ Projet **pas encore sous Git**.
- ❌ Pas de gestion de secrets (le mot de passe e-mail du Jalon 3 sera à protéger).
- ⚠️ Deux `.venv` en double + `requirements.txt` en UTF-16 à nettoyer.
- ⚠️ `data/` (CSV lourds) et `models/` ne doivent pas être committés.

→ **Prochaine action logique : Phase 0.**
