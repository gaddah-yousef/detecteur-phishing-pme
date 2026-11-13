"""Tests de bout en bout sur données exclusivement synthétiques."""

import json

import pytest

from jalon2.entrainer_modele import (
    charger_dataset_etiquete,
    entrainer_et_evaluer,
)
from jalon2.tester_modele import predire_url


def test_entrainement_prediction_et_metriques(tmp_path):
    source = "tests/fixtures/urls_demo.csv"
    destination = tmp_path / "modele.joblib"
    metriques = entrainer_et_evaluer(
        dataset=__import__("pathlib").Path(source),
        output=destination,
        random_state=12,
    )
    assert destination.exists()
    assert 0 <= metriques["f1"] <= 1
    assert metriques["train_samples"] + metriques["test_samples"] == 48
    assert len(metriques["confusion_matrix"]) == 2
    rapport = json.loads(destination.with_suffix(".metrics.json").read_text())
    assert rapport["samples"] == 48
    prediction = predire_url("http://login.example.invalid/verify", destination)
    assert prediction["prediction"] in {"PHISHING", "LEGITIME"}
    assert 0 <= prediction["probabilite_phishing"] <= 1


def test_dataset_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        charger_dataset_etiquete(tmp_path / "absent.csv")


def test_rejects_unrecognized_label(tmp_path):
    source = tmp_path / "unknown.csv"
    source.write_text("URL,Label\nhttps://a.invalid,maybe\n", encoding="utf-8")
    with pytest.raises(ValueError):
        charger_dataset_etiquete(source)
