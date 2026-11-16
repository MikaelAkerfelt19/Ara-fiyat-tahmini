"""Segment, yumuşak km çarpanı, katsayı önceliği ve kalibrasyon testleri."""

import math

import numpy as np
import pytest

from src.ml.config import KM_RAMP, MONOTONIC_MARGIN
from src.ml.localization import (
    calibrate,
    factor_for,
    km_adjustment,
    ramp_fraction,
    segment_of,
    tl_price,
)

# Her öncelik basamağı farklı bir değer verir; hangisinin seçildiği değerden anlaşılır
LOC = {
    "default": 1.0,
    "segments": {"suv": 3.0, "ekonomik": 4.0},
    "overrides": {"Toyota|RAV4": 5.0},
    "km_log_coef": 0.0,  # km çarpanı 1: öncelik testi yalnızca tabanı görür
}


@pytest.mark.parametrize(
    "row, expected",
    [
        ({"brand": "Tesla", "model": "Model 3", "fuel_type": "Elektrik"}, "elektrik"),
        ({"brand": "BMW", "model": "X5", "fuel_type": "Benzin", "body_type": "SUV"}, "premium"),
        ({"brand": "Toyota", "model": "RAV4", "fuel_type": "Benzin", "body_type": "SUV"}, "suv"),
        (
            {"brand": "Honda", "model": "Civic", "fuel_type": "Benzin", "body_type": "Sedan"},
            "ekonomik",
        ),
    ],
)
def test_segment_of(row, expected):
    assert segment_of(row) == expected


@pytest.mark.parametrize(
    "km, expected",
    [
        (0, 0.0),
        (KM_RAMP[0], 0.0),
        (130_000, 0.5),
        (KM_RAMP[1], 1.0),
        (300_000, 1.0),
        (None, 1.0),
        (float("nan"), 1.0),
    ],
)
def test_ramp_fraction(km, expected):
    assert ramp_fraction(km) == pytest.approx(expected)


def test_km_adjustment_never_decreases_and_is_capped():
    coef = 0.25
    values = [km_adjustment(km, coef) for km in range(0, 400_001, 10_000)]
    assert all(b >= a for a, b in zip(values, values[1:], strict=False))
    assert max(values) <= math.exp(coef) + 1e-12
    assert values[0] == 1.0


def test_factor_priority_override_segment_default():
    rav4 = {"brand": "Toyota", "model": "RAV4", "body_type": "SUV", "mileage": 60_000}
    assert factor_for(rav4, LOC) == 5.0  # override
    kia = {"brand": "Kia", "model": "X", "body_type": "SUV", "mileage": 50_000}
    assert factor_for(kia, LOC) == 3.0  # segment
    civic = {"brand": "Honda", "model": "Civic", "body_type": "Sedan", "mileage": 200_000}
    assert factor_for(civic, LOC) == 4.0
    assert factor_for(civic, {**LOC, "segments": {}, "overrides": {}}) == 1.0  # default


def test_factor_applies_km_adjustment():
    civic = {"brand": "Honda", "model": "Civic", "body_type": "Sedan", "mileage": 200_000}
    loc = {**LOC, "km_log_coef": 0.2}
    assert factor_for(civic, loc) == pytest.approx(4.0 * math.exp(0.2))


def test_factor_for_ignores_heavy_damage():
    # Ağır hasar çarpanı yalnızca tl_price'ta uygulanır (çift sayım olmasın)
    clean = {"brand": "Honda", "model": "Civic", "body_type": "Sedan", "mileage": 100_000}
    damaged = {**clean, "title_status": "Ağır hasarlı"}
    assert factor_for(damaged, LOC) == factor_for(clean, LOC)


class _BadModel:
    """Bilerek bozuk model: km arttıkça fiyatı ARTIRIR; ağır hasarlıya ise çok düşük fiyat verir."""

    def predict(self, frame):
        price = 5_000.0 + np.nan_to_num(frame["mileage"].to_numpy(dtype=float)) * 0.1
        return np.where(frame["title_status"] == "Temiz", price, price * 0.1)


_FEATURES = ["mileage", "title_status"]
_CAR = {"brand": "Honda", "model": "Civic", "body_type": "Sedan", "title_status": "Temiz"}


def test_tl_price_envelope_is_non_increasing_in_km():
    prices = [
        tl_price(_BadModel(), _FEATURES, {**_CAR, "mileage": km}, 40.0, LOC)[0]
        for km in range(0, 300_001, 10_000)
    ]
    assert all(b <= a + 1e-9 for a, b in zip(prices, prices[1:], strict=False))


class _BumpyModel:
    """Sahte model: fiyat km'ye göre dalgalanır (ızgara noktaları arasında da)."""

    def predict(self, frame):
        km = np.nan_to_num(frame["mileage"].to_numpy(dtype=float))
        return 10_000.0 + 3_000.0 * np.sin(km / 3_700.0)


def test_tl_price_is_non_increasing_at_any_km_not_only_grid_points():
    # Izgaraya denk gelmeyen km'ler (777'nin katları) de dahil: fiyat asla yükselmez
    prices = [
        tl_price(_BumpyModel(), _FEATURES, {**_CAR, "mileage": km}, 40.0, LOC)[0]
        for km in range(0, 200_001, 777)
    ]
    assert all(b <= a + 1e-9 for a, b in zip(prices, prices[1:], strict=False))


def test_tl_price_returns_usd_at_own_km_and_handles_unknown_km():
    price, usd = tl_price(_BadModel(), _FEATURES, {**_CAR, "mileage": 50_000}, 40.0, LOC)
    assert usd == pytest.approx(5_000.0 + 5_000.0)
    assert price == pytest.approx(5_000.0 * 40.0 * 4.0)  # zarf: 0 km'deki ucuz hal
    price, usd = tl_price(_BadModel(), _FEATURES, {**_CAR, "mileage": None}, 40.0, LOC)
    assert price > 0 and usd > 0


@pytest.mark.parametrize("status", ["Ağır hasarlı", "Ağır hasarlı (onarılmış)"])
def test_heavy_damage_is_exactly_65_percent(status):
    car = {**_CAR, "mileage": 100_000}
    clean, _ = tl_price(_BadModel(), _FEATURES, car, 40.0, LOC)
    damaged, _ = tl_price(_BadModel(), _FEATURES, {**car, "title_status": status}, 40.0, LOC)
    assert damaged == pytest.approx(clean * 0.65)


class _CliffModel:
    """Sahte model: fiyat mileage >= 130k ise 0,7 kat düşer (ABD kırılmasını taklit eder)."""

    def predict(self, frame):
        base = 10_000.0 + (frame["year"].to_numpy(dtype=float) - 2000) * 100
        return np.where(frame["mileage"].to_numpy(dtype=float) >= 130_000, base * 0.7, base)


def test_calibrate_keeps_price_non_increasing_in_km():
    loc = calibrate(_CliffModel(), 50.0, "test")
    assert loc["km_log_coef"] >= 0
    assert loc["model_cliff"] == pytest.approx(0.7)
    assert math.exp(loc["km_log_coef"]) * 0.7 <= MONOTONIC_MARGIN + 1e-9
    assert loc["km_factor_max"] == pytest.approx(math.exp(loc["km_log_coef"]))
    assert loc["km_ramp"] == list(KM_RAMP)
    assert set(loc) >= {"default", "segments", "overrides", "references"}
    assert all({"base", "fitted_tl", "error_pct"} <= set(r) for r in loc["references"])
