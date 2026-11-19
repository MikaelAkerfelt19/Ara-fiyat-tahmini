"""Arayüz geliştirmek için sahte servis. Gerçek servisle aynı imzalar."""

from datetime import datetime

from src.core.mock_data import BRAND_MODELS, BRANDS, MILEAGE_OPTIONS, YEAR_OPTIONS
from src.core.schemas import CarInput, Prediction

_HISTORY: list[dict] = []


def get_options() -> dict[str, list[str]]:
    return {
        "brand": BRANDS,
        "fuel_type": ["Benzin", "Dizel", "Elektrik", "Hibrit"],
        "transmission": ["Manuel", "Otomatik"],
        "condition": ["Hasarlı", "Orta", "Sıfır", "Sıfır gibi", "Çok iyi", "İyi"],
        "drive": ["4x4", "Arkadan itiş", "Önden çekiş"],
        "body_type": ["Hatchback", "SUV", "Sedan", "Station wagon"],
        "title_status": ["Ağır hasarlı", "Ağır hasarlı (onarılmış)", "Temiz"],
        "seller_type": ["Bireysel", "Galeri"],
        "year": YEAR_OPTIONS,
        "mileage": MILEAGE_OPTIONS,
    }


def get_models_for_brand(brand: str) -> list[str]:
    return BRAND_MODELS.get(brand, [])


def get_ranges() -> dict[str, tuple[float, float]]:
    return {"year": (1990, 2026), "mileage": (0, 400_000), "cylinders": (3, 12)}


def predict(car: CarInput) -> Prediction:
    if car.mileage < 0:
        raise ValueError("Kilometre negatif olamaz.")
    price = 30_000 - (2025 - car.year) * 1_200 - car.mileage * 0.04
    price = max(price, 1_500.0) * 40  # USD -> TL
    price = max(price, 60_000.0)
    if car.title_status in ("Ağır hasarlı", "Ağır hasarlı (onarılmış)"):
        price *= 0.65  # gerçek servisle tutarlı: ağır hasarlı araç %35 ucuz
    return Prediction(
        price=price,
        low=price * 0.9,
        high=price * 1.1,
        model_version="mock",
        currency="TRY",
        usd_try=40.0,
    )


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
        "metrics_currency": "USD",
    }
