"""Final modeli eğitir ve kaydeder. Çalıştırma: python -m src.ml.train"""

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_val_predict

from src.core.fx import get_usd_try
from src.db import queries
from src.ml.config import FEATURES, RANDOM_STATE, TARGET
from src.ml.localization import LOCALIZATION_PATH, calibrate
from src.ml.models import BEST_MODEL, make_final_model

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "model.joblib"
META_PATH = MODEL_DIR / "model_meta.json"


def main() -> None:
    df = queries.load_cars()  # temizlenmiş ve filtrelenmiş veri (cars tablosu)
    X, y = df[FEATURES], df[TARGET]

    # 1) Metrikler 5 katlı CV ile: her satır, onu hiç görmemiş bir modelin tahminini alır
    #    (out-of-fold). Veri az olduğu için tek bir train/test bölmesi gürültülü olurdu.
    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    oof = cross_val_predict(make_final_model(), X, y, cv=cv)
    metrics = {
        "mae": float(mean_absolute_error(y, oof)),
        "rmse": float(root_mean_squared_error(y, oof)),
        "r2": float(r2_score(y, oof)),
    }

    # 2) Tahmin aralığı: log ölçeğinde hataların %10 ve %90 yüzdelikleri.
    #    Tahmin anında fiyat * exp(q) ile "olası aralık" verilir.
    residuals = np.log1p(y) - np.log1p(oof)
    q_low, q_high = np.quantile(residuals, [0.10, 0.90])

    # 3) Final: tüm veriyle yeniden eğit (daha çok veri = daha iyi model) ve kaydet
    model = make_final_model()
    model.fit(X, y)
    estimator = model.regressor_.named_steps["reg"]

    now = datetime.now()
    meta = {
        "version": now.strftime("%Y%m%d-%H%M"),
        "model_name": type(estimator).__name__,
        "trained_at": now.isoformat(timespec="seconds"),
        "features": FEATURES,
        "n_train": len(X),
        "interval_log_quantiles": [float(q_low), float(q_high)],
        **metrics,
        "metrics_method": "5-fold CV",
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
        f"5 katlı CV: MAE={metrics['mae']:.0f}  RMSE={metrics['rmse']:.0f}  R²={metrics['r2']:.3f}"
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


if __name__ == "__main__":
    main()
