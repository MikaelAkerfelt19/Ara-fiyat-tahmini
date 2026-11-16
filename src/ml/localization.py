"""Türkiye uyarlaması: USD tahmini TL'ye çevirmek için piyasa katsayısı hesaplar.

fiyat_TL = fiyat_USD x USD/TRY kuru x taban katsayı x km çarpanı x ağır hasar çarpanı.
Katsayılar, elle toplanan Türkiye ilan fiyatları (REFERENCE_CARS) ile modelin aynı arabalar
için USD tahmini karşılaştırılarak eğitimden SONRA bulunur; modelin kendisi ve USD
metrikleri değişmez.
"""

import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.ml.config import (
    FEATURES,
    HEAVY_DAMAGE_DISCOUNT,
    HEAVY_DAMAGE_STATUSES,
    KM_GRID_STEP,
    KM_RAMP,
    MONOTONIC_MARGIN,
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


def ramp_fraction(km) -> float:
    """Km'nin 0 ile 1 arasındaki "rampa konumu": 120k'ya kadar 0, 140k'dan sonra 1.

    Sert bir sınır yerine doğrusal geçiş kullanılır; böylece 119.999 km ile 120.001 km
    arasında fiyat sıçramaz. km bilinmiyorsa 1 döner: verinin çoğunluğu yüksek km'li.
    """
    if km is None or pd.isna(km):
        return 1.0
    low, high = KM_RAMP
    return float(min(1.0, max(0.0, (km - low) / (high - low))))


def km_adjustment(km, log_coef: float) -> float:
    """Km çarpanı = exp(katsayı x rampa). Düşük km'de 1, yüksek km'de exp(katsayı).

    Katsayı >= 0 olduğundan çarpan km arttıkça azalmaz; modelin ABD fiyatındaki düşüşünü
    (km arttıkça fiyat düşer) bu çarpan kısmen geri alır, tamamen değil.
    """
    return math.exp(log_coef * ramp_fraction(km))


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


def _group_geomean(items: list[tuple[str, float]]) -> dict[str, float]:
    """(anahtar, oran) çiftlerini anahtara göre gruplayıp geometrik ortalamasını alır."""
    groups: dict[str, list[float]] = {}
    for key, ratio in items:
        groups.setdefault(key, []).append(ratio)
    return {key: _geometric_mean(v) for key, v in groups.items()}


def _model_cliff(model) -> float:
    """Modelin 120k -> 140k km arasındaki fiyat düşüş oranı (yaklaşık 0,7).

    Her referans araç için iki tahmin alınır (yalnızca km farklı), oranların medyanı
    alınır; medyan, tek bir garip aracın sonucu bozmasını engeller.
    """
    low_km, high_km = KM_RAMP
    frame = _reference_frame()
    at_low = model.predict(frame.assign(mileage=low_km))
    at_high = model.predict(frame.assign(mileage=high_km))
    return float(np.median(np.asarray(at_high, dtype=float) / np.asarray(at_low, dtype=float)))


def calibrate(model, usd_try: float, source: str) -> dict:
    """Referans arabalardan segment, marka+model tabanlarını ve km çarpanını hesaplar."""
    frame = _reference_frame()
    preds = [float(p) for p in model.predict(frame)]
    references = []
    for (brand, name, year, km, _fuel, _body, price_tl), usd, row in zip(
        REFERENCE_CARS, preds, frame.to_dict("records"), strict=True
    ):
        references.append(
            {
                "brand": brand,
                "model": name,
                "year": year,
                "km": km,
                "segment": segment_of(row),
                "price_tl": price_tl,
                "pred_usd": usd,
                "ratio": price_tl / (usd * usd_try),
            }
        )

    # Segment kuklaları + rampa konumu üzerinde en küçük kareler. Segmenti kuklalarla
    # ayırdığımız için km etkisi, segment farkından arındırılmış olarak "c"de toplanır.
    # (Sabit terim yok: kuklalar zaten sabit terimin işini görür.)
    segments = sorted({r["segment"] for r in references})
    design = np.array(
        [
            [float(r["segment"] == s) for s in segments] + [ramp_fraction(r["km"])]
            for r in references
        ]
    )
    target = np.log([r["ratio"] for r in references])
    coefs, *_ = np.linalg.lstsq(design, target, rcond=None)

    # Üst sınır modelin kendi kırılmasından gelir: kırılma x exp(c) <= 0,98 olmalı ki km
    # arttıkça TL fiyat düşsün. Alt sınır 0: km'nin fiyatı artırması anlamsız.
    cliff = _model_cliff(model)
    upper = max(0.0, math.log(MONOTONIC_MARGIN / cliff))
    c = float(min(max(coefs[-1], 0.0), upper))

    # Arındırılmış oran: km etkisi çıkarılınca geriye yalnızca segment/model farkı kalır
    for r in references:
        r["base"] = r["ratio"] / km_adjustment(r["km"], c)

    overrides = {}
    if USE_MODEL_OVERRIDES:
        overrides = _group_geomean([(f"{r['brand']}|{r['model']}", r["base"]) for r in references])
    loc = {
        "computed_at": datetime.now().isoformat(timespec="seconds"),
        "usd_try": usd_try,
        "fx_source": source,
        # Geometrik ortalama: oranlar çarpımsal olduğu için ve uç değere aritmetik
        # ortalamadan daha az duyarlı olduğu için seçildi.
        "default": _geometric_mean([r["base"] for r in references]),
        "segments": _group_geomean([(r["segment"], r["base"]) for r in references]),
        "overrides": overrides,
        "km_ramp": list(KM_RAMP),
        "km_log_coef": c,
        "km_factor_max": math.exp(c),
        "model_cliff": cliff,
    }
    # Sistemin referanslar için verdiği TL, loc tamamlandıktan sonra hesaplanır
    for r, row in zip(references, frame.to_dict("records"), strict=True):
        r["fitted_tl"], _ = tl_price(model, FEATURES, row, usd_try, loc)
        r["error_pct"] = (r["fitted_tl"] / r["price_tl"] - 1) * 100
    loc["references"] = references
    return loc


def factor_for(row: dict, loc: dict) -> float:
    """Toplam katsayı = taban x km çarpanı (ağır hasar çarpanı tl_price'ta).

    Taban önceliği: marka+model > segment > genel.
    """
    override_key = f"{row.get('brand')}|{row.get('model')}"
    if override_key in loc.get("overrides", {}):
        base = float(loc["overrides"][override_key])
    elif segment_of(row) in loc.get("segments", {}):
        base = float(loc["segments"][segment_of(row)])
    else:
        base = float(loc["default"])
    # Ağır hasar çarpanı burada YOK: yalnızca tl_price uygular (çift sayım olmasın)
    return base * km_adjustment(row.get("mileage"), loc["km_log_coef"])


def tl_price(
    model, features: list[str], row: dict, usd_try: float, loc: dict
) -> tuple[float, float]:
    """Aracın TL fiyatını ve kendi km'sindeki USD tahminini döndürür: (fiyat_TL, usd).

    Ağır hasar: model "Temiz" fiyatlar (kendi küçük indirimini eklemesin), en sonda tam
    x(1 - HEAVY_DAMAGE_DISCOUNT) uygulanır; böylece oran her zaman tam %35 olur.
    Km zarfı: aynı aracın daha düşük km'li hali daha ucuz olamaz. Fiyat, 0'dan aracın km'sine
    kadar SABİT 1.000 km adımlı ızgaradaki fiyatların en küçüğüdür. Aracın kendi km'si ızgaraya
    eklenmez: böylece km arttıkça ızgara yalnızca büyür, en küçük değer yalnızca düşebilir ve
    fiyat her km için kesin olarak yükselmez (en fazla 1.000 km'lik yuvarlama farkı olur).
    """
    heavy = row.get("title_status") in HEAVY_DAMAGE_STATUSES
    base_row = {**row, "title_status": "Temiz"} if heavy else dict(row)
    km = base_row.get("mileage")
    if km is None or pd.isna(km):
        grid = [km]  # km bilinmiyor: zarf kurulamaz, tek satır
    else:
        grid = list(range(0, int(km) + 1, KM_GRID_STEP))
    rows = [{**base_row, "mileage": g} for g in grid]
    frame = pd.DataFrame(rows)[features]
    usd = np.asarray(model.predict(frame), dtype=float)
    raw = [u * usd_try * factor_for(r, loc) for u, r in zip(usd, rows, strict=True)]
    price = min(raw)
    if heavy:
        price *= 1 - HEAVY_DAMAGE_DISCOUNT
    # Bilgi amaçlı USD: aracın kendi km'sindeki tahmin
    usd_own = (
        float(usd[-1])
        if km is None or pd.isna(km)
        else _predict_one(model, features, {**base_row, "mileage": km})
    )
    return float(price), usd_own


def _predict_one(model, features: list[str], row: dict) -> float:
    return float(model.predict(pd.DataFrame([row])[features])[0])
