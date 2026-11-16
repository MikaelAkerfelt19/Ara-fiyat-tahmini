"""Türkiye uyarlaması: USD tahmini TL'ye çevirmek için piyasa katsayısı hesaplar.

fiyat_TL = fiyat_USD x USD/TRY kuru x katsayı. Katsayı, elle toplanan Türkiye ilan
fiyatları (REFERENCE_CARS) ile modelin aynı arabalar için USD tahmini karşılaştırılarak
eğitimden SONRA bulunur; modelin kendisi ve USD metrikleri değişmez.
"""

import math
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.ml.config import (
    FEATURES,
    PREMIUM_BRANDS,
    REFERENCE_CARS,
    SUV_BODY_TYPES,
    USE_MODEL_OVERRIDES,
)

LOCALIZATION_PATH = Path("models/localization.json")


def segment_of(row: dict) -> str:
    """Aracın piyasa segmentini bulur. Sıra önemli: elektrik > premium > suv > ekonomik."""
    if row.get("fuel_type") == "Elektrik":
        return "elektrik"
    if row.get("brand") in PREMIUM_BRANDS:
        return "premium"
    if row.get("body_type") in SUV_BODY_TYPES:
        return "suv"
    return "ekonomik"


def _reference_frame() -> pd.DataFrame:
    """REFERENCE_CARS'ı modelin beklediği sütunlara dizer; bilinmeyenler None kalır."""
    rows = [
        {
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": km,
            "fuel_type": fuel,
            "body_type": body,
            "transmission": "Otomatik",
            "title_status": "Temiz",
            "cylinders": None,
            "condition": None,
            "drive": None,
        }
        for brand, model, year, km, fuel, body, _ in REFERENCE_CARS
    ]
    return pd.DataFrame(rows)[FEATURES]


def _geometric_mean(values: list[float]) -> float:
    return math.exp(sum(math.log(v) for v in values) / len(values))


def calibrate(model, usd_try: float, source: str) -> dict:
    """Referans arabalardan segment ve genel katsayıları hesaplar."""
    frame = _reference_frame()
    preds = [float(p) for p in model.predict(frame)]
    references = []
    for (brand, name, year, _km, _fuel, _body, price_tl), usd, row in zip(
        REFERENCE_CARS, preds, frame.to_dict("records"), strict=True
    ):
        references.append(
            {
                "brand": brand,
                "model": name,
                "year": year,
                "segment": segment_of(row),
                "price_tl": price_tl,
                "pred_usd": usd,
                "ratio": price_tl / (usd * usd_try),
            }
        )

    # Geometrik ortalama: oranlar çarpımsal olduğu için ve uç değere aritmetik
    # ortalamadan daha az duyarlı olduğu için seçildi.
    by_segment: dict[str, list[float]] = {}
    for ref in references:
        by_segment.setdefault(ref["segment"], []).append(ref["ratio"])
    overrides = {}
    if USE_MODEL_OVERRIDES:
        overrides = {f"{r['brand']}|{r['model']}": r["ratio"] for r in references}
    return {
        "computed_at": datetime.now().isoformat(timespec="seconds"),
        "usd_try": usd_try,
        "fx_source": source,
        "default": _geometric_mean([r["ratio"] for r in references]),
        "segments": {seg: _geometric_mean(v) for seg, v in by_segment.items()},
        "overrides": overrides,
        "references": references,
    }


def factor_for(row: dict, loc: dict) -> float:
    """Katsayı önceliği: marka+model özel katsayısı > segment > genel."""
    key = f"{row.get('brand')}|{row.get('model')}"
    if key in loc.get("overrides", {}):
        return float(loc["overrides"][key])
    segment = segment_of(row)
    if segment in loc.get("segments", {}):
        return float(loc["segments"][segment])
    return float(loc["default"])
