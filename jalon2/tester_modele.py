"""Évaluation d'une URL sans l'ouvrir ni effectuer de requête réseau.

Attention : joblib exécute du code à la désérialisation. Ne chargez que
des modèles entraînés localement et provenant d'une source de confiance.
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from jalon2.entrainer_modele import MODELE_DEFAUT, extraire_caracteristiques


def predire_url(url: str, modele_path: Path = MODELE_DEFAUT) -> dict:
    """Retourne prédiction, score probabiliste et caractéristiques."""
    modele_path = Path(modele_path)
    if not modele_path.is_file():
        raise FileNotFoundError(
            f"Modèle introuvable : {modele_path}. "
            "Exécutez python -m jalon2.entrainer_modele --dataset <fichier.csv>."
        )
    objet = joblib.load(modele_path)
    modele = objet["modele"]
    features_attendues = objet["features"]
    caracteristiques = extraire_caracteristiques(url)
    colonnes = pd.DataFrame([caracteristiques]).reindex(columns=features_attendues)
    if colonnes.isna().any().any():
        raise ValueError("Le modèle attend des caractéristiques non disponibles.")
    prediction = int(modele.predict(colonnes)[0])
    classes = list(modele.classes_)
    probabilites = modele.predict_proba(colonnes)[0]
    proba = float(probabilites[classes.index(1)])
    return {
        "url": url,
        "prediction": "PHISHING" if prediction else "LEGITIME",
        "probabilite_phishing": round(proba, 4),
        "caracteristiques": caracteristiques,
        "avertissement": "Prédiction indicative d'un modèle pédagogique.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prédire le risque d'une URL.")
    parser.add_argument("url", nargs="?", help="URL à analyser sans l'ouvrir")
    parser.add_argument("--model", type=Path, default=MODELE_DEFAUT)
    args = parser.parse_args()
    url = args.url or input("Entrez une URL à analyser : ").strip()
    if not url:
        parser.error("Une URL est requise.")
    print(json.dumps(predire_url(url, args.model), indent=2,
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
