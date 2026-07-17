"""
Jalon 1 - Script de telechargement d'URLs de phishing
======================================================
Stage PFA ete 2026 - Systeme de detection et d'alerte precoce
des cybermenaces ciblant les PME.

Ce script telecharge la liste des URLs de phishing verifiees et
actuellement en ligne depuis PhishTank, une source publique et
gratuite de Threat Intelligence, puis :
  1. la charge dans un tableau pandas (DataFrame),
  2. affiche un petit resume (nombre d'URLs, marques ciblees...),
  3. sauvegarde le resultat dans un fichier CSV local.

Usage :
    python telecharger_urls.py
"""

import io
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

# La console Windows utilise parfois un encodage limite (cp1252) qui ne
# sait pas afficher certains caracteres presents dans les donnees.
# On force l'affichage en UTF-8 pour eviter les erreurs.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Flux public de PhishTank : URLs de phishing verifiees par la
# communaute et encore en ligne. Gratuit, sans cle d'API.
URL_FLUX = "http://data.phishtank.com/data/online-valid.csv"

# Dossier ou l'on sauvegarde les donnees telechargees.
DOSSIER_DONNEES = Path(__file__).parent / "data"


def telecharger_flux() -> str:
    """Telecharge le flux CSV brut depuis PhishTank et le renvoie en texte."""
    print(f"Telechargement depuis {URL_FLUX} ...")
    reponse = requests.get(URL_FLUX, timeout=120)
    # Leve une erreur claire si le serveur repond autre chose que 200 OK.
    reponse.raise_for_status()
    # Le fichier PhishTank est encode en UTF-8 ; on le precise car
    # requests devine parfois mal l'encodage (accents deformes sinon).
    reponse.encoding = "utf-8"
    print(f"OK : {len(reponse.text):,} caracteres recus.")
    return reponse.text


def corriger_accents(texte: str) -> str:
    """Repare les accents deformes presents dans les donnees PhishTank.

    Certaines valeurs du fichier source sont doublement encodees
    (ex. 'SociÃ©tÃ© GÃ©nÃ©rale' au lieu de 'Société Générale').
    Si la reparation echoue, on garde le texte tel quel.
    """
    try:
        return texte.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texte


def charger_dans_pandas(texte_csv: str) -> pd.DataFrame:
    """Transforme le texte CSV en DataFrame pandas.

    Le fichier PhishTank contient deja une ligne d'en-tete avec les
    colonnes : phish_id, url, phish_detail_url, submission_time,
    verified, verification_time, online, target.
    """
    df = pd.read_csv(io.StringIO(texte_csv))
    df["target"] = df["target"].map(corriger_accents)
    return df


def afficher_resume(df: pd.DataFrame) -> None:
    """Affiche quelques informations simples sur les donnees recuperees."""
    print()
    print("=" * 55)
    print("RESUME DES URLS DE PHISHING RECUPEREES")
    print("=" * 55)
    print(f"Nombre total d'URLs de phishing : {len(df):,}")
    print()
    print("Les 10 marques / services les plus imites :")
    print(df["target"].value_counts().head(10).to_string())
    print()
    print("Apercu des 5 dernieres URLs signalees :")
    apercu = df[["submission_time", "url", "target"]].head(5)
    # On coupe les URLs trop longues pour garder un affichage lisible.
    apercu = apercu.assign(url=apercu["url"].str.slice(0, 70))
    print(apercu.to_string(index=False))
    print("=" * 55)


def sauvegarder(df: pd.DataFrame) -> Path:
    """Sauvegarde le DataFrame dans un CSV date, dans le dossier data/."""
    DOSSIER_DONNEES.mkdir(exist_ok=True)
    horodatage = datetime.now().strftime("%Y-%m-%d_%Hh%M")
    chemin = DOSSIER_DONNEES / f"urls_phishing_{horodatage}.csv"
    df.to_csv(chemin, index=False)
    print(f"\nDonnees sauvegardees dans : {chemin}")
    return chemin


def main() -> None:
    texte_csv = telecharger_flux()
    df = charger_dans_pandas(texte_csv)
    afficher_resume(df)
    sauvegarder(df)


if __name__ == "__main__":
    main()
