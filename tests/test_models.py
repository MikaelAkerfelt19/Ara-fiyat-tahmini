"""Model kurucuların küçük sentetik veride çalıştığını doğrular (data/ veya models/ gerekmez)."""

import numpy as np
import pandas as pd
import pytest

from src.ml.config import CAT_COLS, FEATURES
from src.ml.evaluate import evaluate
from src.ml.models import make_final_model, make_linear_model


@pytest.fixture
def synthetic():
    """40 satırlık sahte veri; bazı sayısal ve kategorik değerler bilerek eksik."""
    rng = np.random.default_rng(0)
    n = 40
    df = pd.DataFrame(
        {
            "year": rng.integers(2000, 2024, n).astype(float),
            "mileage": rng.integers(10_000, 300_000, n).astype(float),
            "cylinders": rng.choice([4.0, 6.0, 8.0], n),
            "brand": rng.choice(["Toyota", "Ford", "BMW"], n).astype(object),
            "model": rng.choice(["A", "B", "C", "D"], n).astype(object),
            "fuel_type": rng.choice(["Benzin", "Dizel"], n).astype(object),
            "transmission": rng.choice(["Otomatik", "Manuel"], n).astype(object),
            "condition": rng.choice(["İyi", "Çok iyi"], n).astype(object),
            "drive": rng.choice(["Önden çekiş", "4x4"], n).astype(object),
            "body_type": rng.choice(["Sedan", "SUV"], n).astype(object),
            "title_status": rng.choice(["Temiz", "Pert kayıtlı"], n).astype(object),
        }
    )[FEATURES]
    df.loc[[1, 5, 9], "year"] = np.nan
    df.loc[[2, 6], "mileage"] = np.nan
    df.loc[[3, 7, 11], "cylinders"] = np.nan
    for col in CAT_COLS:
        df.loc[[0, 4, 8], col] = None
    y = pd.Series(20_000 - (df["year"].fillna(2010) - 2000) * -500 + rng.normal(0, 500, n))
    return df, y.clip(lower=1000)


@pytest.mark.parametrize("maker", [make_linear_model, make_final_model])
def test_model_fits_and_predicts_positive_finite(maker, synthetic):
    X, y = synthetic
    model = maker().fit(X, y)
    pred = model.predict(X)
    assert pred.shape == (len(X),)
    assert np.isfinite(pred).all()
    assert (pred > 0).all()


def test_evaluate_keys(synthetic):
    X, y = synthetic
    metrics = evaluate(make_linear_model().fit(X, y), X, y)
    assert set(metrics) == {"mae", "rmse", "r2"}
    assert all(isinstance(v, float) for v in metrics.values())


def test_final_model_is_monotonic_in_mileage_and_year(synthetic):
    X, y = synthetic
    model = make_final_model().fit(X, y)
    base = X.iloc[[10]].reset_index(drop=True)
    km_grid = pd.concat([base.assign(mileage=km) for km in range(0, 400_001, 20_000)])
    km_pred = model.predict(km_grid)
    assert (np.diff(km_pred) <= 1e-6).all()  # km artınca fiyat artmaz
    year_grid = pd.concat([base.assign(year=yr) for yr in range(1995, 2025)])
    year_pred = model.predict(year_grid)
    assert (np.diff(year_pred) >= -1e-6).all()  # yıl artınca fiyat azalmaz
