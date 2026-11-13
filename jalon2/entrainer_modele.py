"""Extraction des caractéristiques et entraînement du détecteur de phishing."""

import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlparse

MOTS_SUSPECTS = [
    "login",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "password",
    "bank",
    "paypal",
    "signin",
    "confirm",
    "security",
    "support",
    "wallet",
    "bonus",
    "free",
]


def est_adresse_ip(domaine: str) -> int:
    """
    Vérifie si le domaine fourni est une adresse IP.

    Retourne :
        1 si le domaine est une adresse IP valide ;
        0 sinon.
    """
    if not domaine:
        return 0

    # Supprime d'éventuels crochets autour d'une adresse IPv6.
    domaine = domaine.strip("[]")

    try:
        ipaddress.ip_address(domaine)
        return 1
    except ValueError:
        return 0


def contient_mot_suspect(url: str) -> int:
    """
    Vérifie si l'URL contient au moins un mot considéré comme suspect.

    La comparaison ne tient pas compte des majuscules.
    """
    url_minuscule = url.lower()

    return int(
        any(mot in url_minuscule for mot in MOTS_SUSPECTS)
    )


def compter_sous_domaines(domaine: str) -> int:
    """
    Estime le nombre de sous-domaines.

    Exemple :
        login.secure.exemple.com
        -> login et secure sont considérés comme deux sous-domaines.

    Cette méthode reste simple : elle suppose que les deux dernières parties
    correspondent au domaine principal et à son extension.
    """
    if not domaine:
        return 0

    parties = [
        partie
        for partie in domaine.split(".")
        if partie
    ]

    # Une adresse IP ne possède pas de sous-domaines.
    if est_adresse_ip(domaine):
        return 0

    if len(parties) <= 2:
        return 0

    # On ne compte pas "www" comme sous-domaine suspect ou utile ici.
    sous_domaines = parties[:-2]

    if sous_domaines and sous_domaines[0].lower() == "www":
        sous_domaines = sous_domaines[1:]

    return len(sous_domaines)


def extraire_caracteristiques(url: str) -> dict[str, int]:
    """
    Transforme une URL en caractéristiques numériques utilisables par le modèle.

    Args:
        url: URL complète sous forme de chaîne de caractères.

    Returns:
        Dictionnaire contenant les caractéristiques numériques de l'URL.
    """
    if not isinstance(url, str):
        raise TypeError("L'URL doit être une chaîne de caractères.")

    url = url.strip()

    if not url:
        raise ValueError("L'URL ne doit pas être vide.")

    # urlparse reconnaît correctement le domaine si le protocole est présent.
    # Pour une URL sans protocole, on ajoute temporairement //.
    url_pour_analyse = url

    if "://" not in url:
        url_pour_analyse = f"//{url}"

    parsed_url = urlparse(url_pour_analyse)

    domaine = parsed_url.hostname or ""
    chemin = parsed_url.path or ""

    nb_chiffres = sum(
        caractere.isdigit()
        for caractere in url
    )

    utilise_https = int(
        parsed_url.scheme.lower() == "https"
    )

    # Recherche d'un encodage URL tel que %20, %2F ou %3A.
    a_encodage = int(
        re.search(r"%[0-9a-fA-F]{2}", url) is not None
    )

    return {
        "longueur_url": len(url),
        "longueur_domaine": len(domaine),
        "nb_points": url.count("."),
        "nb_tirets": url.count("-"),
        "nb_chiffres": nb_chiffres,
        "nb_slash": url.count("/"),
        "nb_sous_domaines": compter_sous_domaines(domaine),
        "a_arobase": int("@" in url),
        "a_ip": est_adresse_ip(domaine),
        "utilise_https": utilise_https,
        "mot_suspect": contient_mot_suspect(url),

        # On cherche // uniquement dans le chemin.
        # Ainsi, le // normal de http:// ou https:// n'est pas considéré suspect.
        "double_slash": int("//" in chemin),

        # Détection des encodages comme %20 ou %2F.
        "a_encodage": a_encodage,
    }



RACINE = Path(__file__).resolve().parent
DATASET_DEFAUT = RACINE / "data" / "phishing_site_urls.csv"
MODELE_DEFAUT = RACINE / "models" / "phishing_detector.joblib"


def charger_dataset_etiquete(chemin: Path):
    """Charge un CSV avec URL/Label (bad/good, phishing/legitimate ou 1/0)."""
    import pandas as pd

    if not chemin.is_file():
        raise FileNotFoundError(
            f"Dataset absent : {chemin}. Fournissez --dataset <CSV> "
            "ou utilisez tests/fixtures/urls_demo.csv pour la démonstration."
        )
    df = pd.read_csv(chemin, usecols=["URL", "Label"])
    df = df.dropna(subset=["URL", "Label"]).copy()
    df["URL"] = df["URL"].astype(str).str.strip()
    df["Label"] = df["Label"].astype(str).str.strip().str.lower()
    labels = {"bad": 1, "phishing": 1, "1": 1,
              "good": 0, "legitimate": 0, "legitime": 0, "0": 0}
    if not df["Label"].isin(labels).all():
        raise ValueError("Labels attendus : bad/good, phishing/legitimate ou 1/0.")
    df = df.loc[df["URL"].ne("")].copy()
    df["y"] = df["Label"].map(labels).astype(int)

    # La même URL ne doit jamais se trouver dans le train et dans le test.
    # Écarter les cas contradictoires, puis dédupliquer les URLs restantes.
    ambigu = df.groupby("URL")["y"].nunique()
    df = df.loc[~df["URL"].isin(ambigu[ambigu > 1].index)]
    df = df.drop_duplicates(subset=["URL"]).reset_index(drop=True)
    if df["y"].nunique() != 2 or df["y"].value_counts().min() < 3:
        raise ValueError("Au moins 3 URLs distinctes par classe sont nécessaires.")
    return df


def entrainer_et_evaluer(dataset: Path, output: Path, test_size: float = 0.25,
                         random_state: int = 42) -> dict:
    """Entraîne un baseline supervisé et persiste modèle + métriques.

    Les métriques mesurent uniquement le jeu d'évaluation fourni.
    Elles ne constituent pas une certification de détection en production.
    """
    import joblib
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        accuracy_score, confusion_matrix, f1_score,
        precision_score, recall_score,
    )
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    if not 0.1 <= test_size <= 0.5:
        raise ValueError("test_size doit être compris entre 0.1 et 0.5.")
    df = charger_dataset_etiquete(dataset)
    x = pd.DataFrame([extraire_caracteristiques(url) for url in df["URL"]])
    y = df["y"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, stratify=y, random_state=random_state
    )
    model = Pipeline([
        ("scale", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1500, class_weight="balanced",
                                           random_state=random_state)),
    ])
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {
        "samples": len(df),
        "train_samples": len(x_train),
        "test_samples": len(x_test),
        "positive_fraction": round(float(y.mean()), 4),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=[0, 1]).tolist(),
        "dataset": str(dataset),
        "random_state": random_state,
        "model": "StandardScaler + LogisticRegression (class_weight=balanced)",
        "note": "Validation pédagogique, non représentative d'un trafic de production.",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"modele": model, "features": list(x.columns),
                 "metrics": metrics}, output)
    metrics_path = output.with_suffix(".metrics.json")
    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metrics


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Entraîne un classifieur pédagogique d'URLs de phishing."
    )
    parser.add_argument("--dataset", type=Path, default=DATASET_DEFAUT)
    parser.add_argument("--output", type=Path, default=MODELE_DEFAUT)
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--demo-features", action="store_true",
                        help="Affiche les caractéristiques d'une URL fictive.")
    args = parser.parse_args()
    if args.demo_features:
        exemple = "http://203.0.113.10/verify-account"
        print(json.dumps(extraire_caracteristiques(exemple), indent=2))
        return
    print(json.dumps(
        entrainer_et_evaluer(args.dataset, args.output, args.test_size,
                            args.random_state),
        indent=2, ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
