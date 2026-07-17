from pathlib import Path

import pandas as pd

DATASET_PATH = Path("data/phishing_site_urls.csv")


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {DATASET_PATH.resolve()}"
        )

    df = pd.read_csv(DATASET_PATH)

    print("\n=== Dimensions du dataset ===")
    print(f"Nombre de lignes : {df.shape[0]}")
    print(f"Nombre de colonnes : {df.shape[1]}")

    print("\n=== Noms des colonnes ===")
    print(df.columns.tolist())

    print("\n=== Premières lignes ===")
    print(df.head())

    print("\n=== Répartition des classes ===")
    print(df["Label"].value_counts())

    print("\n=== Répartition en pourcentage ===")
    print(df["Label"].value_counts(normalize=True).mul(100).round(2))

    print("\n=== Valeurs manquantes ===")
    print(df.isnull().sum())

    print("\n=== Nombre de doublons ===")
    print(df.duplicated().sum())


if __name__ == "__main__":
    main()