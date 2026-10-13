"""Arayüz geliştirmek için sahte servis. Gerçek servisle aynı imzalar."""

from datetime import datetime

from src.core.schemas import CarInput, Prediction

_MODELS = {
    "BMW": ["320i", "520d", "X5"],
    "Ford": ["Fiesta", "Focus", "Kuga"],
    "Toyota": ["Corolla", "C-HR", "Yaris"],
}
_HISTORY: list[dict] = []


def get_options() -> dict[str, list[str]]:
    return {
        "brand": sorted(_MODELS),
        "fuel_type": ["Benzin", "Dizel", "Elektrik", "Hibrit"],
        "transmission": ["Manuel", "Otomatik"],
    }


def get_models_for_brand(brand: str) -> list[str]:
    return _MODELS.get(brand, [])


def get_ranges() -> dict[str, tuple[float, float]]:
    return {"year": (1995, 2025), "mileage": (0, 400_000)}


def predict(car: CarInput) -> Prediction:
    if car.mileage < 0:
        raise ValueError("Kilometre negatif olamaz.")
    price = 30_000 - (2025 - car.year) * 1_200 - car.mileage * 0.04
    price = max(price, 1_500.0)
    return Prediction(price=price, low=price * 0.9, high=price * 1.1, model_version="mock")


def save_prediction(car: CarInput, pred: Prediction) -> None:
    row = {"created_at": datetime.now().isoformat(timespec="seconds"), **car.to_dict()}
    row["price"] = round(pred.price)
    _HISTORY.insert(0, row)


def get_history(limit: int = 20) -> list[dict]:
    return _HISTORY[:limit]


def get_model_info() -> dict:
    return {
        "model_name": "mock",
        "version": "mock",
        "trained_at": None,
        "mae": None,
        "rmse": None,
        "r2": None,
        "n_train": 0,
    }
