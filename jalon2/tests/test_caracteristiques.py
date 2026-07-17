"""Tests unitaires de l'extraction des caractéristiques d'URL."""

import pytest

from jalon2.entrainer_modele import (
    est_adresse_ip,
    extraire_caracteristiques,
)


def test_longueur_url():
    """Vérifie le calcul de la longueur complète de l'URL."""
    url = "http://exemple.com"

    features = extraire_caracteristiques(url)

    assert features["longueur_url"] == len(url)


def test_detecte_https():
    """Vérifie la détection des protocoles HTTPS et HTTP."""
    features_https = extraire_caracteristiques(
        "https://banque.com"
    )
    features_http = extraire_caracteristiques(
        "http://banque.com"
    )

    assert features_https["utilise_https"] == 1
    assert features_http["utilise_https"] == 0


def test_detecte_adresse_ip_dans_url():
    """Vérifie qu'une adresse IP utilisée comme domaine est détectée."""
    url_avec_ip = "http://42.231.90.113/login.php"
    url_avec_domaine = "http://www.google.com"

    assert extraire_caracteristiques(url_avec_ip)["a_ip"] == 1
    assert extraire_caracteristiques(url_avec_domaine)["a_ip"] == 0


def test_fonction_est_adresse_ip():
    """Teste directement la fonction est_adresse_ip."""
    assert est_adresse_ip("42.231.90.113") == 1
    assert est_adresse_ip("192.168.1.1") == 1
    assert est_adresse_ip("www.google.com") == 0
    assert est_adresse_ip("exemple.com") == 0


def test_detecte_mot_suspect():
    """Vérifie la détection d'un mot suspect."""
    url_suspecte = "http://site.com/login"
    url_normale = "http://site.com/accueil"

    assert extraire_caracteristiques(url_suspecte)["mot_suspect"] == 1
    assert extraire_caracteristiques(url_normale)["mot_suspect"] == 0


def test_detecte_mot_suspect_en_majuscules():
    """Vérifie que la détection ignore les majuscules."""
    url = "http://site.com/VERIFY"

    assert extraire_caracteristiques(url)["mot_suspect"] == 1


def test_compte_tirets():
    """Vérifie le comptage des tirets."""
    url = "http://secure-paypal-login.com"

    features = extraire_caracteristiques(url)

    assert features["nb_tirets"] == 2


def test_compte_points():
    """Vérifie le comptage des points."""
    url = "http://a-b-c.d.e.com"

    features = extraire_caracteristiques(url)

    assert features["nb_points"] == 3


def test_compte_chiffres():
    """Vérifie le comptage des chiffres."""
    url = "http://site123.com/login2026"

    features = extraire_caracteristiques(url)

    # 123 contient 3 chiffres et 2026 en contient 4.
    assert features["nb_chiffres"] == 7


def test_compte_slash():
    """Vérifie le comptage des slashs."""
    url = "http://site.com/account/login"

    features = extraire_caracteristiques(url)

    assert features["nb_slash"] == url.count("/")


def test_detecte_arobase():
    """Vérifie la présence du caractère @."""
    url_avec_arobase = (
        "http://google.com@site-dangereux.com/login"
    )
    url_sans_arobase = "https://google.com"

    assert (
        extraire_caracteristiques(
            url_avec_arobase
        )["a_arobase"]
        == 1
    )

    assert (
        extraire_caracteristiques(
            url_sans_arobase
        )["a_arobase"]
        == 0
    )


def test_detecte_double_slash_dans_chemin():
    """Vérifie la détection d'un double slash dans le chemin."""
    url_suspecte = "http://site.com/account//login"
    url_normale = "http://site.com/account/login"

    assert (
        extraire_caracteristiques(
            url_suspecte
        )["double_slash"]
        == 1
    )

    assert (
        extraire_caracteristiques(
            url_normale
        )["double_slash"]
        == 0
    )


def test_protocole_non_considere_comme_double_slash():
    """
    Vérifie que le // de https:// n'est pas considéré comme suspect.
    """
    url = "https://site.com/account/login"

    features = extraire_caracteristiques(url)

    assert features["double_slash"] == 0


def test_detecte_encodage_url():
    """Vérifie la détection d'un encodage comme %20 ou %2F."""
    url_encodee = "https://site.com/%2Flogin%20secure"
    url_normale = "https://site.com/login"

    assert (
        extraire_caracteristiques(
            url_encodee
        )["a_encodage"]
        == 1
    )

    assert (
        extraire_caracteristiques(
            url_normale
        )["a_encodage"]
        == 0
    )


def test_longueur_domaine():
    """Vérifie le calcul de la longueur du domaine."""
    url = "https://exemple.com/login"

    features = extraire_caracteristiques(url)

    assert features["longueur_domaine"] == len("exemple.com")


def test_nombre_sous_domaines():
    """Vérifie le calcul du nombre de sous-domaines."""
    url = "https://login.secure.exemple.com/account"

    features = extraire_caracteristiques(url)

    assert features["nb_sous_domaines"] == 2


def test_www_non_compte_comme_sous_domaine():
    """Vérifie que www n'est pas compté comme sous-domaine."""
    url = "https://www.google.com"

    features = extraire_caracteristiques(url)

    assert features["nb_sous_domaines"] == 0


def test_url_simple_sans_signes_suspects():
    """Vérifie plusieurs caractéristiques d'une URL normale."""
    url = "https://www.google.com"

    features = extraire_caracteristiques(url)

    assert features["utilise_https"] == 1
    assert features["a_ip"] == 0
    assert features["a_arobase"] == 0
    assert features["mot_suspect"] == 0
    assert features["nb_tirets"] == 0
    assert features["nb_chiffres"] == 0
    assert features["double_slash"] == 0
    assert features["a_encodage"] == 0


def test_url_suspecte_complete():
    """Vérifie plusieurs indicateurs d'une URL suspecte."""
    url = (
        "http://42.231.90.113/"
        "secure-paypal-login//verify%20account"
    )

    features = extraire_caracteristiques(url)

    assert features["utilise_https"] == 0
    assert features["a_ip"] == 1
    assert features["mot_suspect"] == 1
    assert features["nb_tirets"] == 2
    assert features["double_slash"] == 1
    assert features["a_encodage"] == 1


def test_url_vide_refusee():
    """Vérifie qu'une URL vide est refusée."""
    with pytest.raises(ValueError):
        extraire_caracteristiques("")


def test_type_invalide_refuse():
    """Vérifie qu'une valeur non textuelle est refusée."""
    with pytest.raises(TypeError):
        extraire_caracteristiques(None)