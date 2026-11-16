"""Final modeli eğitir ve kaydeder. Çalıştırma: python -m src.ml.train"""

import json
import time
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold

from src.core.fx import get_usd_try
from src.db import queries
from src.ml.config import FEATURES, KAGGLE_WEIGHT, RANDOM_STATE, TARGET
from src.ml.localization import LOCALIZATION_PATH, calibrate
from src.ml.models import BEST_MODEL, make_final_model

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "model.joblib"
META_PATH = MODEL_DIR / "model_meta.json"
N_SPLITS = 5


def _fit(train: pd.DataFrame, weights: np.ndarray):
    """Modeli satır ağırlıklarıyla eğitir (Kaggle satırları daha ağır basar)."""
    model = make_final_model()
    model.fit(train[FEATURES], train[TARGET].astype(float), reg__sample_weight=weights)
    return model


def _weights(frame: pd.DataFrame) -> np.ndarray:
    """Kaggle ilanı KAGGLE_WEIGHT, diğerleri 1. Asıl hedef bizim yarışma verisi olduğu için
    model ona daha çok uysun."""
    return np.where(frame["source"] == "kaggle", KAGGLE_WEIGHT, 1.0)


def main() -> None:
    started = time.perf_counter()
    df = queries.load_cars()  # temizlenmiş ve filtrelenmiş veri (cars tablosu)
    kaggle = df[df["source"] == "kaggle"].reset_index(drop=True)
    others = df[df["source"] != "kaggle"].reset_index(drop=True)
    print(f"Veri: {len(kaggle)} Kaggle + {len(others)} vehicles ilanı")

    # 1) Ölçüm yalnızca Kaggle ilanları üzerinde yapılır (asıl hedef onlar). Her katta
    #    eğitim = diğer Kaggle katları (ağırlık 5) + tüm vehicles (ağırlık 1); tahmin edilen
    #    kat modelin hiç görmediği Kaggle ilanlarıdır (out-of-fold). vehicles ilanları
    #    Kaggle ile çakışmayacak şekilde load_data'da temizlendi, yani sızıntı yok.
    cv = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    y = kaggle[TARGET].to_numpy(float)
    oof = np.zeros(len(kaggle))
    for fold, (tr, te) in enumerate(cv.split(kaggle), start=1):
        t0 = time.perf_counter()
        train = pd.concat([kaggle.iloc[tr], others], ignore_index=True)
        model = _fit(train, _weights(train))
        oof[te] = model.predict(kaggle.iloc[te][FEATURES])
        print(f"  kat {fold}/{N_SPLITS} bitti ({time.perf_counter() - t0:.0f} sn)", flush=True)

    metrics = {
        "mae": float(mean_absolute_error(y, oof)),
        "rmse": float(root_mean_squared_error(y, oof)),
        "r2": float(r2_score(y, oof)),
    }
    median_ape = float(np.median(np.abs(oof - y) / y))

    # 2) Tahmin aralığı: log ölçeğinde hataların %10 ve %90 yüzdelikleri.
    #    Tahmin anında fiyat * exp(q) ile "olası aralık" verilir.
    residuals = np.log1p(y) - np.log1p(oof)
    q_low, q_high = np.quantile(residuals, [0.10, 0.90])

    # 3) Final: tüm veriyle yeniden eğit (daha çok veri = daha iyi model) ve kaydet
    print("Final model eğitiliyor...", flush=True)
    full = pd.concat([kaggle, others], ignore_index=True)
    model = _fit(full, _weights(full))
    estimator = model.regressor_.named_steps["reg"]

    now = datetime.now()
    meta = {
        "version": now.strftime("%Y%m%d-%H%M"),
        "model_name": type(estimator).__name__,
        "trained_at": now.isoformat(timespec="seconds"),
        "features": FEATURES,
        "n_train": len(full),
        "n_kaggle": len(kaggle),
        "n_vehicles": len(others),
        "interval_log_quantiles": [float(q_low), float(q_high)],
        **metrics,
        "median_ape": median_ape,
        "metrics_method": "5-fold CV",
        "metrics_on": "Kaggle ilanları (5 katlı, vehicles eğitimde)",
        "metrics_currency": "USD",
    }

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    META_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    # Veritabanına da kaydedilir; arayüzün "Model hakkında" bölümü buradan okuyabilir
    queries.insert_model_run(meta, params=estimator.get_params())

    # 4) Türkiye uyarlaması: referans ilan fiyatlarından TL katsayıları (model değişmez)
    rate, source = get_usd_try()
    loc = calibrate(model, rate, source)
    LOCALIZATION_PATH.write_text(json.dumps(loc, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Model kaydedildi: {MODEL_PATH} (sürüm {meta['version']}, {BEST_MODEL})")
    print(
        f"5 katlı CV (Kaggle ilanları): MAE={metrics['mae']:.0f}  RMSE={metrics['rmse']:.0f}  "
        f"R²={metrics['r2']:.3f}  medyan % hata={median_ape:.1%}"
    )
    print(f"Tahmin aralığı (log): {q_low:.3f} .. {q_high:.3f}")
    print(f"Kur: {rate:.4f} ({source})")
    print("Referans tablosu (araç, km, gerçek TL, sistemin TL'si, % hata):")
    for r in loc["references"]:
        print(
            f"  {r['brand']} {r['model']} {r['year']} {r['km']:,} km: "
            f"{r['price_tl']:,} TL, {r['fitted_tl']:,.0f} TL, {r['error_pct']:+.1f}%"
        )
    print("Segment tabanları:", {k: round(v, 3) for k, v in loc["segments"].items()})
    print(f"Genel taban: {loc['default']:.3f}")
    print(f"km_factor_max: {loc['km_factor_max']:.3f}  model_cliff: {loc['model_cliff']:.3f}")
    print(f"Toplam süre: {time.perf_counter() - started:.0f} sn")


if __name__ == "__main__":
    main()
