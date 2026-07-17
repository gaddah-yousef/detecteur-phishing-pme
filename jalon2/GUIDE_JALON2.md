# Guide pas à pas — Jalon 2 : Construire un premier détecteur

*À faire soi-même, étape par étape. Objectif : entraîner un modèle simple qui reconnaît une URL de phishing, et surtout **être capable de l'expliquer** au point de contrôle.*

---

## Étape 0 — Préparer l'environnement (15 min)

1. Ouvrir un terminal et installer scikit-learn :
   ```
   pip install scikit-learn
   ```
2. Vérifier que ça marche :
   ```
   python -c "import sklearn; print(sklearn.__version__)"
   ```
3. Travailler dans le dossier `jalon2/` (ce dossier).

---

## Étape 1 — Comprendre la démarche avant de coder (1/2 journée)

Avant d'écrire une ligne de code, il faut pouvoir répondre à ces questions avec vos propres mots (l'encadrant les posera) :

- **Qu'est-ce qu'une classification binaire ?** → Apprendre à ranger chaque URL dans une des deux classes : *phishing* ou *légitime*.
- **Qu'est-ce qu'une caractéristique (feature) ?** → Un nombre calculé à partir de l'URL (sa longueur, son nombre de points...) que le modèle utilise pour décider. Le modèle ne « lit » pas l'URL comme un humain : il ne voit que ces nombres.
- **Pourquoi séparer entraînement et test ?** → Pour vérifier que le modèle sait généraliser à des URLs **jamais vues**. Évaluer sur les données d'entraînement, c'est comme réviser avec les réponses de l'examen : le score ne veut rien dire.

Lecture recommandée : le tutoriel officiel scikit-learn (https://scikit-learn.org/stable/tutorial/index.html), sections « An introduction to machine learning » et « Supervised learning ».

---

## Étape 2 — Récupérer un jeu de données étiqueté (1/2 journée)

Deux options proposées par la fiche, en choisir **UNE** :

**Option A (recommandée) — Kaggle : « Phishing Site URLs »**
- Chercher sur https://www.kaggle.com/datasets le dataset *Phishing Site URLs* (fichier `phishing_site_urls.csv`, ~549 000 lignes).
- Il contient 2 colonnes : `URL` (l'adresse brute) et `Label` (`bad` = phishing, `good` = légitime).
- Avantage pédagogique : les URLs sont **brutes**, c'est vous qui calculerez les caractéristiques (étape 3) — vous comprendrez donc chaque nombre que le modèle utilise.
- Nécessite un compte Kaggle gratuit pour télécharger. Placer le CSV dans `jalon2/data/`.

**Option B — UCI : « PhiUSIIL Phishing URL Dataset »**
- https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset (~235 000 lignes).
- Les caractéristiques sont **déjà calculées** (54 colonnes). Plus rapide, mais moins formateur : vous utiliserez des features sans les avoir construites.

**Premier réflexe une fois le fichier téléchargé** — l'explorer avec pandas :
```python
import pandas as pd
df = pd.read_csv("data/phishing_site_urls.csv")
print(df.shape)                    # combien de lignes / colonnes ?
print(df.head())                   # à quoi ressemblent les données ?
print(df["Label"].value_counts())  # combien de phishing vs légitime ?
```
Notez la répartition des classes : si un déséquilibre existe (ex. 70 % / 30 %), il faudra le garder en tête pour lire les résultats.

---

## Étape 3 — Transformer chaque URL en nombres (1 à 2 jours)

*(Étape nécessaire seulement avec l'option A ; c'est le cœur du travail.)*

Le modèle a besoin de nombres. Reprenez les signes suspects identifiés dans votre note du Jalon 1 et transformez-les en fonctions Python. Idées de caractéristiques simples :

| Caractéristique | Intuition |
|---|---|
| Longueur de l'URL | Les URLs de phishing sont souvent très longues |
| Nombre de points `.` | Beaucoup de sous-domaines trompeurs |
| Nombre de tirets `-` | Fréquents dans les domaines imités (`secure-paypal-login`) |
| Nombre de chiffres | Domaines jetables générés automatiquement |
| Présence de `@` | Tout ce qui précède `@` est ignoré par le navigateur |
| Présence d'une adresse IP | `http://42.231.90.113/...` = très suspect |
| Commence par `https` (0/1) | Le phishing utilise plus souvent `http` |
| Mot suspect (`login`, `verify`, `secure`, `account`, `update`...) | Vocabulaire typique des fausses pages |

Squelette de code à compléter vous-même :
```python
import re

def extraire_caracteristiques(url: str) -> dict:
    return {
        "longueur": len(url),
        "nb_points": url.count("."),
        "nb_tirets": url.count("-"),
        "nb_chiffres": sum(c.isdigit() for c in url),
        "a_arobase": int("@" in url),
        "a_ip": int(bool(re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url))),
        # ... ajoutez les vôtres
    }

# Appliquer à tout le DataFrame :
X = pd.DataFrame([extraire_caracteristiques(u) for u in df["URL"]])
y = (df["Label"] == "bad").astype(int)   # 1 = phishing, 0 = légitime
```

Astuce : commencez avec 4–5 caractéristiques, faites tourner toute la chaîne jusqu'au bout, puis revenez en ajouter. *Une petite brique qui marche vaut mieux qu'une grande à moitié faite.*

---

## Étape 4 — Séparer entraînement et test (1 heure, mais capital)

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,        # 20 % gardés de côté pour le test
    random_state=42,      # pour des résultats reproductibles
    stratify=y,           # garde la même proportion phishing/légitime des deux côtés
)
```

C'est **LE point que l'encadrant vérifiera**. Règle d'or : les données de test ne servent qu'à la toute fin, une seule fois, pour mesurer. Jamais pour entraîner.

---

## Étape 5 — Entraîner UN modèle simple (1/2 journée)

La fiche demande UN seul modèle. Deux choix possibles :

- **Arbre de décision** (`DecisionTreeClassifier`) — recommandé : il se lit comme un organigramme de questions (« la longueur dépasse-t-elle 54 ? oui → ... »), donc très facile à expliquer à l'oral.
- **Régression logistique** (`LogisticRegression`) — calcule une probabilité de phishing à partir d'une somme pondérée des caractéristiques.

```python
from sklearn.tree import DecisionTreeClassifier

modele = DecisionTreeClassifier(max_depth=5, random_state=42)
modele.fit(X_train, y_train)   # l'apprentissage se fait ici, sur le TRAIN uniquement
```

Pourquoi `max_depth=5` ? Un arbre sans limite apprend « par cœur » les données d'entraînement (c'est le **surapprentissage** / *overfitting*). Limiter la profondeur le force à retenir des règles générales. Testez plusieurs valeurs et observez l'effet.

---

## Étape 6 — Évaluer et lire les résultats (1/2 journée)

```python
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

y_pred = modele.predict(X_test)

print("Taux de réussite :", accuracy_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["légitime", "phishing"]))
```

Savoir lire la **matrice de confusion** (4 cases) :

|  | Prédit légitime | Prédit phishing |
|---|---|---|
| **Réellement légitime** | Vrai négatif ✓ | **Faux positif** (fausse alerte) |
| **Réellement phishing** | **Faux négatif** (menace ratée !) | Vrai positif ✓ |

À méditer et à mettre dans vos phrases d'explication : pour une PME, quel est le pire — une fausse alerte, ou une URL de phishing qui passe inaperçue ? (Le faux négatif est généralement plus grave → regardez le **rappel/recall** de la classe phishing, pas seulement le taux de réussite global.)

Piège classique : si 90 % des URLs du dataset sont légitimes, un modèle idiot qui répond toujours « légitime » a déjà 90 % de réussite. D'où l'importance du rapport complet, pas juste de l'accuracy.

---

## Étape 7 — Expliquer son modèle (1/2 journée)

Pour l'arbre de décision :
```python
from sklearn.tree import export_text
print(export_text(modele, feature_names=list(X.columns)))   # l'arbre en texte lisible

# Quelles caractéristiques comptent le plus ?
import pandas as pd
print(pd.Series(modele.feature_importances_, index=X.columns).sort_values(ascending=False))
```

Test amusant et parlant pour la démo : prenez 2–3 URLs réelles du CSV téléchargé au Jalon 1 (`jalon1/data/`), extrayez leurs caractéristiques et faites-les prédire par votre modèle.

---

## Étape 8 — Rédiger le livrable

Le livrable = **un script** (`entrainer_modele.py`) qui enchaîne : chargement → caractéristiques → séparation train/test → entraînement → affichage du taux de réussite, **plus quelques phrases d'explication** (en commentaires ou dans un petit `.md`) :

- quel dataset, combien d'exemples, quelle répartition des classes ;
- quelles caractéristiques et pourquoi ;
- quel modèle et comment il fonctionne, dit avec vos mots ;
- les résultats (accuracy + matrice de confusion) et ce qu'ils signifient ;
- une limite honnête (ex. « le modèle rate X % des phishing, or c'est le cas le plus grave »).

## Checklist avant d'envoyer à l'encadrant

- [ ] Le script tourne de bout en bout sans erreur
- [ ] Le test est bien séparé de l'entraînement (et je sais expliquer pourquoi)
- [ ] Je sais expliquer chaque caractéristique choisie
- [ ] Je sais expliquer comment mon modèle décide
- [ ] Je sais lire la matrice de confusion et dire ce qu'est un faux négatif
- [ ] J'ai noté mes questions pour le point de suivi

## Planning suggéré (1er → 15 août)

| Jours | Quoi |
|---|---|
| 1–2 | Étapes 0–1 : environnement + notions |
| 3–4 | Étape 2 : dataset trouvé, exploré avec pandas |
| 5–7 | Étape 3 : extraction des caractéristiques |
| 8–9 | Étapes 4–5 : séparation + entraînement |
| 10–11 | Étape 6 : évaluation, lecture des résultats |
| 12–13 | Étape 7 : interprétation, tests sur les URLs du Jalon 1 |
| 14–15 | Étape 8 : rédaction, checklist, envoi |

*Conseil final : pour les questions Machine Learning, la co-encadrante Pr. Mehdia Ajana est la personne à solliciter.*
