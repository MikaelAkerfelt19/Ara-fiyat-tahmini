"""Gerçek servis testleri: geçici veritabanı ve küçük model, ağ yok."""

import json

import joblib
import numpy as np
import pandas as pd
import pytest

from src.core import service
from src.core.errors import ModelNotReadyError
from src.core.schemas import CarInput
from src.db import schema
from src.ml.config import FEATURES
from src.ml.models import make_final_model


def _cars(n: int = 40) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    year = rng.integers(2005, 2022, n)
    return pd.DataFrame(
        {
            "year": year,
            "mileage": rng.integers(10_000, 250_000, n),
            "cylinders": rng.choice([4, 6], n),
            "brand": rng.choice(["Honda", "Toyota"], n),
            "model": rng.choice(["Civic", "Corolla"], n),
            "fuel_type": "Benzin",
            "transmission": "Otomatik",
            "condition": "İyi",
            "drive": "Önden çekiş",
            "body_type": "Sedan",
            "title_status": "Temiz",
            "price": (year - 1995) * 700.0 + rng.normal(0, 300, n) + 1000,
        }
    )


@pytest.fixture
def ready(tmp_path, monkeypatch):
    df = _cars()
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "cars.db")
    with schema.connect() as conn:
        schema.create_tables(conn)
        df.to_sql("cars", conn, index=False)
    model = make_final_model().fit(df[FEATURES], df["price"])
    joblib.dump(model, tmp_path / "model.joblib")
    meta = {
        "version": "test",
        "model_name": "HistGradientBoostingRegressor",
        "trained_at": "2026-11-16T10:00:00",
        "features": FEATURES,
        "n_train": len(df),
        "interval_log_quantiles": [-0.2, 0.2],
        "mae": 1.0,
        "rmse": 2.0,
        "r2": 0.5,
    }
    (tmp_path / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    loc = {"default": 1.5, "segments": {"ekonomik": 1.2}, "overrides": {}}
    (tmp_path / "loc.json").write_text(json.dumps(loc), encoding="utf-8")
    monkeypatch.setattr(service, "MODEL_PATH", tmp_path / "model.joblib")
    monkeypatch.setattr(service, "META_PATH", tmp_path / "meta.json")
    monkeypatch.setattr(service, "LOCALIZATION_PATH", tmp_path / "loc.json")
    monkeypatch.setattr(service, "get_usd_try", lambda: (40.0, "test"))
    service._load_model.cache_clear()
    yield
    service._load_model.cache_clear()


@pytest.fixture
def car():
    return CarInput("Honda", "Civic", 2015, 100_000, "Benzin", "Otomatik", body_type="Sedan")


def test_predict_returns_positive_try_price_with_interval(ready, car):
    pred = service.predict(car)
    assert pred.price > 0
    assert pred.low <= pred.price <= pred.high
    assert pred.currency == "TRY"
    assert pred.usd_try == 40.0


def test_negative_mileage_is_rejected(ready, car):
    car.mileage = -5
    with pytest.raises(ValueError):
        service.predict(car)


def test_missing_model_files(tmp_path, monkeypatch, car):
    for name in ("MODEL_PATH", "META_PATH", "LOCALIZATION_PATH"):
        monkeypatch.setattr(service, name, tmp_path / "yok")
    service._load_model.cache_clear()
    try:
        with pytest.raises(ModelNotReadyError):
            service.predict(car)
        info = service.get_model_info()
        assert set(info) >= {"model_name", "version", "mae", "n_train"}
        assert all(v is None for v in info.values())
    finally:
        service._load_model.cache_clear()


def test_history_newest_first_and_options_without_model(ready, car):
    pred = service.predict(car)
    service.save_prediction(car, pred)
    car.model = "Corolla"
    service.save_prediction(car, pred)
    history = service.get_history(2)
    assert [row["model"] for row in history] == ["Corolla", "Civic"]
    assert "model" not in service.get_options()
