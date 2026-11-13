"""Tableau de bord de CTI et classification lexicale d'URLs (sans requête vers les URLs)."""

from pathlib import Path

import pandas as pd
import streamlit as st

from jalon2.entrainer_modele import MODELE_DEFAUT
from jalon2.tester_modele import predire_url

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DONNEES = RACINE / "jalon1" / "data"

st.set_page_config(page_title="Phishing PME — CTI Lab", page_icon="🛡️", layout="wide")
st.title("🛡️ Phishing PME — Threat Intelligence & ML Lab")
st.caption("Projet pédagogique. Une prédiction ne constitue pas un verdict de sécurité.")


@st.cache_data(ttl=600)
def charger_urls(chemin: str) -> pd.DataFrame:
    data = pd.read_csv(chemin, low_memory=False)
    colonnes = {"submission_time", "url", "target"}
    if not colonnes.issubset(data.columns):
        raise ValueError("Colonnes manquantes dans le CSV : submission_time, url, target.")
    return data


st.header("1. Signalements de phishing")
fichiers = sorted(DOSSIER_DONNEES.glob("urls_phishing_*.csv"))
if fichiers:
    try:
        df = charger_urls(str(fichiers[-1]))
        col1, col2, col3 = st.columns(3)
        col1.metric("Signalements", f"{len(df):,}")
        col2.metric("Marques distinctes", int(df["target"].nunique()))
        col3.metric("Dernier signalement", str(df["submission_time"].max())[:10])
        st.subheader("Échantillon de signalements")
        st.dataframe(
            df[["submission_time", "url", "target"]].head(50),
            use_container_width=True,
            hide_index=True,
        )
        st.subheader("Top 10 des marques imitées")
        marques = df.loc[df["target"].ne("Other"), "target"].value_counts().head(10)
        st.bar_chart(marques)
        st.info("Les URLs sont des indicateurs bruts : ne les ouvrez pas dans votre navigateur.")
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        st.error(f"Impossible de lire le CSV de signalements : {exc}")
else:
    st.info(
        "Aucun flux local. La collecte est facultative : "
        "exécutez `python jalon1/telecharger_urls.py` si le fournisseur est disponible."
    )

st.divider()
st.header("2. Classification d'une URL (analyse statique)")
st.write(
    "L'URL saisie est analysée sous forme de texte : "
    "**aucune connexion n'est envoyée au domaine**."
)
if MODELE_DEFAUT.is_file():
    url = st.text_input(
        "URL de test", value="https://www.example.com/",
        help="Utilisez de préférence un exemple synthétique ou un domaine de test."
    )
    if st.button("Analyser", type="primary"):
        try:
            resultat = predire_url(url, MODELE_DEFAUT)
            st.metric("Classe prédite", resultat["prediction"])
            st.metric("Score estimé de phishing",
                      f"{resultat['probabilite_phishing']:.1%}")
            st.warning(resultat["avertissement"])
            with st.expander("Caractéristiques utilisées"):
                st.json(resultat["caracteristiques"])
        except (ValueError, OSError, KeyError) as exc:
            st.error(f"Échec de l'analyse : {exc}")
else:
    st.warning(
        "Modèle non entraîné. Lancez `python -m jalon2.entrainer_modele "
        "--dataset <CSV étiqueté>`, puis actualisez cette page. "
        "Le fichier d'exemple fourni est **synthétique** et ne mesure pas "
        "la qualité réelle d'une détection."
    )
