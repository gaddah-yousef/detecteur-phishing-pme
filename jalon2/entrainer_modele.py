"""Extraction des caractéristiques et entraînement du détecteur de phishing."""

import ipaddress
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


if __name__ == "__main__":
    url_exemple = (
        "http://42.231.90.113/"
        "secure-paypal-login//verify%20account"
    )

    caracteristiques = extraire_caracteristiques(url_exemple)

    print("URL analysée :", url_exemple)
    print("Caractéristiques :")

    for nom, valeur in caracteristiques.items():
        print(f"- {nom}: {valeur}")