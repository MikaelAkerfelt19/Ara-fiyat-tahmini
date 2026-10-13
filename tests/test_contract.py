"""Servis sözleşmesini ve sahte servisin davranışlarını doğrula."""

import importlib
import inspect

import pytest

from src.core import api, mock_service, service
from src.core.schemas import CarInput, Prediction


@pytest.fixture
def car():
    return CarInput("Toyota", "Corolla", 2020, 50_000, "Benzin", "Manuel")


@pytest.mark.parametrize(
    "name",
    [
        "get_options",
        "get_models_for_brand",
        "get_ranges",
        "predict",
        "save_prediction",
        "get_history",
        "get_model_info",
    ],
)
def test_service_signatures_match(name):
    assert inspect.signature(getattr(mock_service, name)) == inspect.signature(
        getattr(service, name)
    )


def test_options_are_sorted_unique_and_model_is_dependent():
    options = mock_service.get_options()
    assert "brand" in options
    assert "model" not in options
    for values in options.values():
        assert values == sorted(set(values))


def test_unknown_brand_has_no_models():
    assert mock_service.get_models_for_brand("Yok") == []


def test_ranges_have_increasing_bounds():
    ranges = mock_service.get_ranges()
    assert ranges
    for lower, upper in ranges.values():
        assert lower < upper


def test_prediction_has_price_within_interval(car):
    prediction = mock_service.predict(car)
    assert isinstance(prediction, Prediction)
    assert prediction.low <= prediction.price <= prediction.high


def test_negative_mileage_is_rejected(car):
    car.mileage = -1
    with pytest.raises(ValueError):
        mock_service.predict(car)


def test_history_returns_latest_predictions_first(car, monkeypatch):
    monkeypatch.setattr(mock_service, "_HISTORY", [])
    mock_service.save_prediction(car, Prediction(20_000.0, None, None, "mock"))
    car.model = "Yaris"
    mock_service.save_prediction(car, Prediction(25_000.0, None, None, "mock"))
    history = mock_service.get_history(2)
    assert len(history) == 2
    assert [row["model"] for row in history] == ["Yaris", "Corolla"]
    assert [row["price"] for row in history] == [25_000, 20_000]
    assert all(row["created_at"] for row in history)


def test_model_info_has_contract_keys():
    assert set(mock_service.get_model_info()) == {
        "model_name",
        "version",
        "trained_at",
        "mae",
        "rmse",
        "r2",
        "n_train",
    }


@pytest.mark.parametrize("use_mock, expected", [("1", mock_service), ("0", service)])
def test_api_selects_service_from_environment(use_mock, expected, monkeypatch):
    try:
        monkeypatch.setenv("USE_MOCK", use_mock)
        assert importlib.reload(api).service is expected
    finally:
        monkeypatch.undo()
        importlib.reload(api)
