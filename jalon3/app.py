"""Tableau de bord - Détecteur de phishing pour PME (Jalon 3, étape 1)."""

from pathlib import Path

import pandas as pd
import streamlit as st

# Dossier racine du projet (parent du dossier jalon3/), pour que l'app
# fonctionne quel que soit le dossier depuis lequel on la lance.
RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DONNEES = RACINE / "jalon1" / "data"

st.set_page_config(page_title="Détecteur de phishing PME", page_icon="🎣")

st.title("🎣 Détecteur de phishing pour PME")
st.write("Prototype de détection et d'alerte précoce — Stage PFA 2026")


@st.cache_data
def charger_urls() -> pd.DataFrame:
    """Charge le CSV d'URLs le plus récent téléchargé au Jalon 1."""
    fichiers = sorted(DOSSIER_DONNEES.glob("urls_phishing_*.csv"))
    if not fichiers:
        raise FileNotFoundError(
            "Aucun fichier urls_phishing_*.csv dans jalon1/data/. "
            "Exécute d'abord jalon1/telecharger_urls.py."
        )
    return pd.read_csv(fichiers[-1])


try:
    df = charger_urls()
except FileNotFoundError as erreur:
    st.error(str(erreur))
    st.stop()

# --- Trois indicateurs clés côte à côte ---
col1, col2, col3 = st.columns(3)
col1.metric("URLs de phishing", f"{len(df):,}")
col2.metric("Marques ciblées", df["target"].nunique())
col3.metric("Dernier signalement", str(df["submission_time"].max())[:10])

# --- Tableau des derniers signalements ---
st.subheader("Derniers signalements (PhishTank)")
st.dataframe(df[["submission_time", "url", "target"]].head(50))

# --- Marques les plus imitées ---
st.subheader("Top 10 des marques imitées")
top_marques = (
    df.loc[df["target"] != "Other", "target"]
    .value_counts()
    .head(10)
)
st.bar_chart(top_marques)
