"""Collecte d'indicateurs URL pour un laboratoire de Threat Intelligence.

Télécharge uniquement un flux CSV reconnu ; n'ouvre jamais les URLs listées.
"""

import io
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# Privilégier HTTPS : ne pas télécharger un flux d'indicateurs de sécurité en clair.
URL_FLUX = "https://data.phishtank.com/data/online-valid.csv"
DOSSIER_DONNEES = Path(__file__).resolve().parent / "data"
COLONNES_REQUISES = {"url", "target", "submission_time"}


def telecharger_flux() -> str:
    """Récupère le CSV et échoue clairement si le fournisseur est inaccessible."""
    try:
        reponse = requests.get(
            URL_FLUX,
            timeout=(10, 120),
            headers={"User-Agent": "SME-Phishing-Research/1.0 (educational)"},
        )
        reponse.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Flux PhishTank indisponible. Vérifiez l'accès HTTPS, les conditions "
            "du fournisseur ou utilisez un CSV de démonstration local."
        ) from exc
    reponse.encoding = "utf-8"
    return reponse.text


def corriger_accents(texte: str) -> str:
    """Conserve le texte d'origine si l'encodage est déjà correct."""
    if not isinstance(texte, str):
        return texte
    if "Ã" not in texte and "Â" not in texte:
        return texte
    try:
        return texte.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texte


def charger_dans_pandas(texte_csv: str) -> pd.DataFrame:
    """Parse le CSV de source en vérifiant son schéma minimal."""
    df = pd.read_csv(io.StringIO(texte_csv), low_memory=False)
    manquantes = COLONNES_REQUISES - set(df.columns)
    if manquantes:
        raise ValueError(f"Colonnes manquantes dans le flux: {sorted(manquantes)}")
    df["target"] = df["target"].map(corriger_accents)
    df["url"] = df["url"].fillna("").astype(str).str.strip()
    df = df.loc[df["url"].ne("")].drop_duplicates(subset=["url"])
    return df


def afficher_resume(df: pd.DataFrame) -> None:
    print(f"Signalements uniques : {len(df):,}")
    print("\nMarques les plus imitées :")
    print(df["target"].fillna("Inconnue").value_counts().head(10).to_string())
    print("\nDerniers enregistrements :")
    print(df[["submission_time", "target"]].head(5).to_string(index=False))


def sauvegarder(df: pd.DataFrame) -> Path:
    DOSSIER_DONNEES.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d_%Hh%M%S_UTC")
    chemin = DOSSIER_DONNEES / f"urls_phishing_{horodatage}.csv"
    df.to_csv(chemin, index=False)
    return chemin


def main() -> None:
    df = charger_dans_pandas(telecharger_flux())
    afficher_resume(df)
    print(f"Enregistré : {sauvegarder(df)}")


if __name__ == "__main__":
    main()
