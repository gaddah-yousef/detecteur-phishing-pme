from pathlib import Path

import joblib
import pandas as pd
from entrainer_modele import extraire_caracteristiques

MODEL_PATH = Path("models/phishing_detector.joblib")


def predire_url(url: str) -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Le modèle n'existe pas. Exécute d'abord entrainer_modele.py."
        )

    objet = joblib.load(MODEL_PATH)

    modele = objet["modele"]
    features_attendues = objet["features"]

    caracteristiques = extraire_caracteristiques(url)

    X_url = pd.DataFrame([caracteristiques])
    X_url = X_url[features_attendues]

    prediction = int(modele.predict(X_url)[0])

    probabilites = modele.predict_proba(X_url)[0]
    probabilite_phishing = float(probabilites[1])

    resultat = "PHISHING" if prediction == 1 else "LÉGITIME"

    print("\n=== Analyse de l'URL ===")
    print(f"URL : {url}")
    print(f"Prédiction : {resultat}")
    print(
        f"Probabilité estimée de phishing : "
        f"{probabilite_phishing:.2%}"
    )

    print("\nCaractéristiques extraites :")
    for nom, valeur in caracteristiques.items():
        print(f"- {nom}: {valeur}")


def main() -> None:
    url = input("Entrez une URL à analyser : ").strip()

    if not url:
        print("Aucune URL fournie.")
        return

    predire_url(url)


if __name__ == "__main__":
    main()