"""Gerçek servis. Fonksiyon imzaları docs/CONTRACT.md ile aynıdır."""

import json
import math
from datetime import date
from functools import lru_cache
from pathlib import Path

import joblib

from src.core.errors import ModelNotReadyError
from src.core.fx import get_usd_try
from src.core.schemas import CarInput, Prediction
from src.db import queries
from src.ml.config import CAT_COLS, NUM_COLS
from src.ml.localization import tl_price

MODEL_PATH = Path("models/model.joblib")
META_PATH = Path("models/model_meta.json")
LOCALIZATION_PATH = Path("models/localization.json")


# ---------- Veritabanından gelenler ----------


def get_options() -> dict[str, list[str]]:
    # model markaya bağlı olduğu için seçenek listesinde yok
    options = queries.distinct_values([c for c in CAT_COLS if c != "model"])
    # Marka listesi de model eşiğiyle filtrelenir: modeli olmayan marka gösterilmez.
    options["brand"] = queries.brands_with_models()

    # Yıl ve kilometre de seçenekli alanlar: değerler doğrudan cars tablosundan.
    years = queries.distinct_values(["year"]).get("year", [])
    options["year"] = sorted(
        int(y) for y in years if 1950 <= int(y) <= date.today().year + 1
    )
    _, km_max = queries.numeric_ranges(["mileage"])["mileage"]
    options["mileage"] = list(range(0, int(km_max) + 1, 5_000))
    return options


def get_models_for_brand(brand: str) -> list[str]:
    return queries.models_for_brand(brand)


def get_ranges() -> dict[str, tuple[float, float]]:
    return queries.numeric_ranges(NUM_COLS)


def save_prediction(car: CarInput, pred: Prediction) -> None:
    # Geçmişte TL kaydedilir, arayüz de TL gösterir
    queries.insert_prediction(car.to_dict(), pred.price, pred.model_version)


def get_history(limit: int = 20) -> list[dict]:
    return queries.recent_predictions(limit)


# ---------- Model ----------


@lru_cache(
    maxsize=1
)  # dosyalar bir kez yüklenir; yeni model için Streamlit'i yeniden başlat
def _load_model() -> tuple:
    paths = (MODEL_PATH, META_PATH, LOCALIZATION_PATH)
    if not all(p.exists() for p in paths):
        raise ModelNotReadyError(
            "Model bulunamadı. Önce: python -m src.db.load_data ve python -m src.ml.train"
        )
    model = joblib.load(MODEL_PATH)
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    loc = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    return model, meta, loc


def _validate(car: CarInput) -> None:
    if car.mileage < 0:
        raise ValueError("Kilometre negatif olamaz.")
    # Yüzdelik aralığa göre reddetmiyoruz: yeni arabalar %99'un üstünde kalabilir.
    last_year = date.today().year + 1
    if not 1930 <= car.year <= last_year:
        raise ValueError(f"Model yılı 1930-{last_year} aralığında olmalı.")


def predict(car: CarInput) -> Prediction:
    _validate(car)
    model, meta, loc = _load_model()
    rate, _ = get_usd_try()
    # TL fiyat = USD tahmin x kur x katsayı; km zarfı ve ağır hasar kuralı tl_price'ta
    price, _usd = tl_price(model, meta["features"], car.to_dict(), rate, loc)
    q_low, q_high = meta["interval_log_quantiles"]
    return Prediction(
        price=price,
        low=price * math.exp(q_low),
        high=price * math.exp(q_high),
        model_version=meta["version"],
        currency="TRY",
        usd_try=rate,
    )


def get_model_info() -> dict:
    keys = ["model_name", "version", "trained_at", "mae", "rmse", "r2", "n_train"]
    try:
        _, meta, _ = _load_model()
    except ModelNotReadyError:
        return {**dict.fromkeys(keys), "metrics_currency": None}
    return {**{k: meta.get(k) for k in keys}, "metrics_currency": "USD"}
