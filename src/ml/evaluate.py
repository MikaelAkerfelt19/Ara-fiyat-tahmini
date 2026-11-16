"""Model başarısını ölçen yardımcı fonksiyonlar (USD cinsinden)."""

from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold, cross_validate

from src.ml.config import RANDOM_STATE


def evaluate(model, X, y) -> dict[str, float]:
    """Eğitilmiş modeli verilen veride ölçer: MAE ve RMSE dolar, R² birimsizdir."""
    pred = model.predict(X)
    return {
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(root_mean_squared_error(y, pred)),
        "r2": float(r2_score(y, pred)),
    }


def cv_scores(model, X, y, cv: int = 5) -> dict[str, float]:
    """K katlı çapraz doğrulama; her metrik için ortalama ve standart sapma döndürür.

    Veri az olduğundan tek bir train/test bölmesi şansa bağlıdır; 5 farklı bölmenin
    ortalaması daha güvenilir bir tahmin verir. shuffle=True ve sabit random_state ile
    bölmeler her çalıştırmada aynıdır, yani modeller adil karşılaştırılır.
    """
    folds = KFold(n_splits=cv, shuffle=True, random_state=RANDOM_STATE)
    # sklearn "büyük = iyi" kuralı için hata metriklerini negatif verir; aşağıda işareti çeviriyoruz
    res = cross_validate(
        model,
        X,
        y,
        cv=folds,
        scoring={
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
            "r2": "r2",
        },
        n_jobs=-1,
    )
    out: dict[str, float] = {}
    for name, sign in (("mae", -1), ("rmse", -1), ("r2", 1)):
        values = sign * res[f"test_{name}"]
        out[f"{name}_mean"] = float(values.mean())
        out[f"{name}_std"] = float(values.std())
    return out
