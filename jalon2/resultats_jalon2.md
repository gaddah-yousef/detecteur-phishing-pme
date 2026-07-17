# Résultats du Jalon 2 — Un premier détecteur d'URLs de phishing

*Stage PFA été 2026 — Jalon 2 (1er au 15 août) · Livrable : script d'entraînement + explication des résultats*

Les chiffres ci-dessous sont les résultats réels affichés par `entrainer_modele.py`.

---

## 1. Le jeu de données

J'ai utilisé le dataset **« Phishing Site URLs »** de Kaggle : un fichier CSV de
**549 354 URLs brutes**, chacune étiquetée `good` (légitime) ou `bad` (phishing).

Après nettoyage (suppression des lignes vides et des doublons), il reste
**507 196 URLs** :

| Classe             | Nombre  | Proportion |
|---                 |---      |---         |
| `good`  (légitime) | 392 897 | ≈ 77 %     |
| `bad`   (phishing) | 114 299 | ≈ 23 %     |

Les classes sont **déséquilibrées** : c'est important, car un modèle qui répondrait
toujours « légitime » aurait déjà 77 % de réussite sans rien détecter. J'en tiens
compte avec l'option `class_weight="balanced"` du modèle, et en lisant les résultats
classe par classe plutôt que le score global seul.

## 2. Les caractéristiques (features)

Un modèle de Machine Learning ne « lit » pas une URL comme un humain : il ne voit
que des nombres. J'ai donc transformé chaque URL en **14 caractéristiques
numériques**, inspirées des signes suspects identifiés dans ma note du Jalon 1 :
longueur de l'URL et du domaine, nombre de points, de tirets, de chiffres, de `/`,
nombre de sous-domaines, présence d'un `@`, d'une adresse IP brute, du HTTPS,
de mots suspects (`login`, `verify`, `secure`, `paypal`...), d'un double slash dans
le chemin et d'encodage `%`.

Après entraînement, les caractéristiques **les plus décisives** pour le modèle sont :

1. `mot_suspect` (≈ 55 % de l'importance) — la présence d'un mot comme *login*,
   *verify*, *secure* dans l'URL ;
2. `nb_tirets` (≈ 16 %) — les domaines imités du type `secure-paypal-login` ;
3. `nb_chiffres` (≈ 14 %) — les domaines jetables générés automatiquement ;
4. `a_ip` (≈ 6 %) — une adresse IP à la place d'un nom de domaine.

Cela correspond bien à l'intuition « métier » du Jalon 1, ce qui est rassurant.

## 3. Le modèle choisi : un arbre de décision

J'ai entraîné **un seul modèle simple**, comme demandé : un
`DecisionTreeClassifier` de scikit-learn. Un arbre de décision fonctionne comme un
organigramme de questions oui/non apprises automatiquement, par exemple :
*« l'URL contient-elle un mot suspect ? »* → si oui, *« a-t-elle plus de 17
chiffres ? »* → ... jusqu'à une décision finale (phishing ou légitime). C'est le
modèle le plus facile à expliquer, et on peut afficher ses règles avec
`export_text()`.

Deux réglages importants :
- `max_depth=5` : sans limite de profondeur, l'arbre apprendrait « par cœur » les
  données d'entraînement (**surapprentissage**) au lieu de retenir des règles
  générales ;
- `class_weight="balanced"` : compense le déséquilibre 77/23 des classes.

## 4. La démarche d'évaluation : entraînement et test séparés

J'ai séparé les données avec `train_test_split` : **80 % pour l'entraînement**
(405 756 URLs) et **20 % pour le test** (101 440 URLs), avec `stratify=y` pour
garder la même proportion phishing/légitime des deux côtés.

Le jeu de test n'est utilisé **qu'une seule fois, à la fin**, pour mesurer la
performance sur des URLs que le modèle n'a **jamais vues**. Évaluer sur les données
d'entraînement reviendrait à réviser avec les réponses de l'examen : le score
serait artificiellement bon et ne dirait rien de la réalité.

## 5. Les résultats

**Taux de réussite global (accuracy) : 81,3 %** sur les 101 440 URLs de test.

Matrice de confusion :

|  | Prédit légitime | Prédit phishing |
|---|---|---|
| **Réellement légitime** (78 580) | 70 232 ✓ (vrais négatifs) | 8 348 (faux positifs = fausses alertes) |
| **Réellement phishing** (22 860) | **10 643 (faux négatifs = menaces ratées !)** | 12 217 ✓ (vrais positifs) |

Lecture par classe :
- Classe **légitime** : rappel ≈ 89 % — le modèle reconnaît bien les URLs normales.
- Classe **phishing** : précision ≈ 59 %, **rappel ≈ 53 %** — le modèle ne détecte
  qu'environ **une URL de phishing sur deux**.

## 6. Limite honnête et pistes d'amélioration

Le chiffre de 81 % d'accuracy paraît bon, mais il est **trompeur** : pour l'usage
visé (protéger une PME), l'erreur la plus grave est le **faux négatif** — une URL
de phishing qui passe inaperçue et n'déclenche aucune alerte. Or mon modèle en
laisse passer 10 643 sur 22 860, soit près d'une sur deux.

Explications probables : mes 14 caractéristiques restent simples (des comptages de
caractères) et beaucoup d'URLs de phishing courtes et « propres » leur échappent ;
un arbre limité à 5 niveaux ne peut exprimer que des règles grossières.

Pistes pour la suite (Jalon 3 et au-delà) :
- ajouter des caractéristiques plus fines (analyse du nom de domaine, TLD suspects
  comme `.click` ou `.xyz`, longueur du chemin vs du domaine...) ;
- tester une profondeur d'arbre un peu plus grande, en surveillant le
  surapprentissage ;
- dans le tableau de bord, afficher la **probabilité** de phishing plutôt qu'une
  décision binaire, pour laisser une marge d'appréciation à l'utilisateur.

---

## Comment reproduire ces résultats

```bash
cd jalon2
python explorer_dataset.py    # exploration du dataset
python entrainer_modele.py    # entraînement + évaluation + sauvegarde du modèle
python tester_modele.py       # tester une URL à la main
```

*Fichiers associés : `entrainer_modele.py` (script principal),
`models/phishing_detector.joblib` (modèle sauvegardé, régénérable).*
