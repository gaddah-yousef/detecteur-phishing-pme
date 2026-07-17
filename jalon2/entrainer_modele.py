import ipaddress
import re
from pathlib import Path
from urllib.parse import urlparse

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text


DATASET_PATH = Path("data/phishing_site_urls.csv")
MODEL_PATH = Path("models/phishing_detector.joblib")

MOTS_SUSPECTS = (
    "login",
    "signin",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "bank",
    "password",
    "confirm",
    "paypal",
    "wallet",
    "support",
    "security",
)


def normaliser_url(url: str) -> str:
    """Nettoie légèrement une URL avant l'extraction."""
    return str(url).strip().lower()


def extraire_nom_hote(url: str) -> str:
    """
    Extrait le nom d'hôte.

    urlparse comprend mieux une URL lorsqu'un schéma
    comme http:// ou https:// est présent.
    """
    url_complete = url

    if not url.startswith(("http://", "https://")):
        url_complete = f"http://{url}"

    try:
        return urlparse(url_complete).hostname or ""
    except ValueError:
        return ""


def est_adresse_ip(nom_hote: str) -> int:
    """Retourne 1 si le nom d'hôte est une adresse IP valide."""
    try:
        ipaddress.ip_address(nom_hote)
        return 1
    except ValueError:
        return 0


def extraire_caracteristiques(url: str) -> dict[str, int]:
    """Transforme une URL brute en caractéristiques numériques."""
    url = normaliser_url(url)
    nom_hote = extraire_nom_hote(url)

    mots_trouves = sum(mot in url for mot in MOTS_SUSPECTS)

    return {
        "longueur_url": len(url),
        "longueur_domaine": len(nom_hote),
        "nb_points": url.count("."),
        "nb_tirets": url.count("-"),
        "nb_chiffres": sum(caractere.isdigit() for caractere in url),
        "nb_slash": url.count("/"),
        "nb_sous_domaines": max(nom_hote.count(".") - 1, 0),
        "a_arobase": int("@" in url),
        "a_ip": est_adresse_ip(nom_hote),
        "utilise_https": int(url.startswith("https://")),
        "mot_suspect": int(any(mot in url for mot in MOTS_SUSPECTS)),
        "nb_mots_suspects": mots_trouves,
        "a_double_slash_chemin": int(
            bool(re.search(r"https?://.+//", url))
        ),
        "a_encodage_pourcent": int("%" in url),
    }


def charger_dataset() -> pd.DataFrame:
    """Charge et contrôle le fichier CSV."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {DATASET_PATH.resolve()}"
        )

    df = pd.read_csv(DATASET_PATH)

    colonnes_requises = {"URL", "Label"}
    colonnes_manquantes = colonnes_requises - set(df.columns)

    if colonnes_manquantes:
        raise ValueError(
            f"Colonnes manquantes : {sorted(colonnes_manquantes)}"
        )

    df = df[["URL", "Label"]].dropna()
    df = df.drop_duplicates()

    labels_valides = {"good", "bad"}
    labels_trouves = set(df["Label"].astype(str).str.lower().unique())

    if not labels_trouves.issubset(labels_valides):
        raise ValueError(
            f"Labels inattendus dans le dataset : {labels_trouves}"
        )

    return df


def main() -> None:
    print("1. Chargement du dataset...")
    df = charger_dataset()

    print(f"Nombre d'URLs après nettoyage : {len(df)}")
    print(df["Label"].value_counts())

    print("\n2. Extraction des caractéristiques...")
    X = pd.DataFrame(
        [extraire_caracteristiques(url) for url in df["URL"]]
    )

    y = (
        df["Label"]
        .astype(str)
        .str.lower()
        .eq("bad")
        .astype(int)
    )

    print(f"Dimensions de X : {X.shape}")
    print(f"Nombre de labels : {y.shape[0]}")
    print("\nCaractéristiques utilisées :")
    print(X.columns.tolist())

    print("\n3. Séparation entraînement/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print(f"Taille du train : {len(X_train)}")
    print(f"Taille du test : {len(X_test)}")

    print("\n4. Entraînement de l'arbre de décision...")
    modele = DecisionTreeClassifier(
        max_depth=5,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=42,
    )

    modele.fit(X_train, y_train)

    print("\n5. Évaluation sur le jeu de test...")
    y_pred = modele.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    matrice = confusion_matrix(y_test, y_pred)

    print(f"\nAccuracy : {accuracy:.4f}")

    print("\nMatrice de confusion :")
    print(matrice)

    print("\nRapport de classification :")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["légitime", "phishing"],
            digits=4,
        )
    )

    print("\n6. Importance des caractéristiques...")
    importances = pd.Series(
        modele.feature_importances_,
        index=X.columns,
    ).sort_values(ascending=False)

    print(importances)

    print("\n7. Règles apprises par l'arbre...")
    print(
        export_text(
            modele,
            feature_names=list(X.columns),
        )
    )

    print("\n8. Sauvegarde du modèle...")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    objet_a_sauvegarder = {
        "modele": modele,
        "features": list(X.columns),
        "mots_suspects": MOTS_SUSPECTS,
    }

    joblib.dump(objet_a_sauvegarder, MODEL_PATH)

    print(f"Modèle sauvegardé dans : {MODEL_PATH.resolve()}")


if __name__ == "__main__":
    main()