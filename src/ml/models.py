"""Model kurucu fonksiyonlar. Hepsi ham (clean edilmiş) X alır, USD fiyat döndürür."""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)

from src.ml.config import CAT_COLS, NUM_COLS, RANDOM_STATE

# Seçilen model: büyük veri için sıra kodlamalı HistGB (make_big_hist_gb). Aşağıdaki
# BEST_PARAMS, küçük Kaggle verisiyle yapılan eski arama sonucudur (notebooks/03_modelleme.ipynb:
# 5 katlı CV MAE varsayılan 6028 -> ayarlı 5881 USD); notebook karşılaştırması için kalır.
BEST_MODEL = "big_hist_gb"
BEST_PARAMS: dict = {
    "learning_rate": 0.03,
    "max_iter": 400,
    "max_leaf_nodes": 15,
    "min_samples_leaf": 5,
    "l2_regularization": 0,
}


def _to_object(df):
    """Sütunları object türüne çevirir. Adlı fonksiyon: lambda joblib ile kaydedilemez."""
    return df.astype(object)


def make_preprocessor(scale: bool) -> ColumnTransformer:
    """Sayısal ve kategorik sütunları modele hazırlar.

    Sayısal: eksikler medyanla doldurulur (uç değerlere dayanıklı). Doğrusal modeller için
    ayrıca ölçeklenir (scale=True); ağaçlar ölçeğe duyarsızdır.
    Kategorik: eksikler "Bilinmiyor" sınıfı olur, sonra one-hot. 5'ten az görülen sınıflar
    tek "seyrek" grupta birleşir, eğitimde görülmeyen yeni sınıf hata vermez.
    """
    num_steps = [SimpleImputer(strategy="median")]
    if scale:
        num_steps.append(StandardScaler())
    cat_steps = [
        # None/NaN karışık sütunlar imputer'da tür sorunu çıkarmasın diye object'e çevrilir
        FunctionTransformer(_to_object, feature_names_out="one-to-one"),
        SimpleImputer(strategy="constant", fill_value="Bilinmiyor"),
        OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=5, sparse_output=False),
    ]
    return ColumnTransformer(
        [
            ("num", Pipeline([(f"s{i}", s) for i, s in enumerate(num_steps)]), NUM_COLS),
            ("cat", Pipeline([(f"s{i}", s) for i, s in enumerate(cat_steps)]), CAT_COLS),
        ]
    )


def _wrap(reg, scale: bool, pandas_out: bool = False) -> TransformedTargetRegressor:
    """Ön işleme + modeli birleştirir ve fiyatı log ölçeğinde öğretir.

    Fiyat sağa çarpık olduğu için log1p ile öğrenilir; böylece model oransal hatayı
    küçültür ve pahalı birkaç araba eğitimi domine etmez. Tahmin expm1 ile dolara döner.
    Ön işleme pipeline içinde olduğundan CV'de sızıntı olmaz.
    """
    pre = make_preprocessor(scale)
    if pandas_out:
        # Kısıt sözlüğü sütunları adla bulur; adların korunması için pandas çıktısı gerekir
        pre = pre.set_output(transform="pandas")
    pipe = Pipeline([("pre", pre), ("reg", reg)])
    return TransformedTargetRegressor(regressor=pipe, func=np.log1p, inverse_func=np.expm1)


def make_baseline() -> DummyRegressor:
    """Hiçbir şey öğrenmeyen referans: hep eğitim medyanını söyler (log yok)."""
    return DummyRegressor(strategy="median")


def make_linear_model(alpha: float = 1.0) -> TransformedTargetRegressor:
    """Ridge (L2 cezalı doğrusal regresyon); ölçekleme gerekir."""
    return _wrap(Ridge(alpha=alpha), scale=True)


def make_random_forest(**params) -> TransformedTargetRegressor:
    """Random Forest: çok sayıda ağacın ortalaması; ölçekleme gerekmez."""
    reg = RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1, **params)
    return _wrap(reg, scale=False)


def make_hist_gb(**params) -> TransformedTargetRegressor:
    """Histogram tabanlı gradient boosting: ağaçlar sırayla öncekinin hatasını düzeltir."""
    # Km artınca fiyat düşer, yıl artınca artar. Az veride ağaçlar bu yönlerde zikzak çizer;
    # kısıt eğriyi monoton tutar. Sabittir: dışarıdan ezilemez.
    reg = HistGradientBoostingRegressor(
        random_state=RANDOM_STATE,
        monotonic_cst={"num__mileage": -1, "num__year": 1},
        **params,
    )
    return _wrap(reg, scale=False, pandas_out=True)


def _to_float(df):
    """Sayısal sütunları float'a çevirir (None/Int64 -> NaN). Adlı fonksiyon: joblib için."""
    return df.apply(pd.to_numeric, errors="coerce").astype(float)


def make_big_hist_gb() -> TransformedTargetRegressor:
    """Büyük veri (300 bin ilan) için HistGB: sıra kodlama + yerel kategori desteği.

    One-hot, ~10 bin farklı model adıyla binlerce sütun açar ve belleğe sığmaz. Bunun yerine
    kategoriler sıra numarasına çevrilir ve HistGB bunları kendi kategori desteğiyle ayırır:
    hızlı ve bellek dostu. Nadir (20'den az görülen) sınıflar tek "seyrek" grupta birleşir,
    en çok 250 sınıf tutulur, eğitimde görülmeyen yeni sınıf hata vermez (NaN olur).
    Yüksek öğrenme adımı sayısı (1500) ve küçük hız (0,05), büyük veride ince ayrım içindir;
    erken durdurma kapalı: iterasyon sayısı sabit, sonuç tekrarlanabilir.
    """
    cat = Pipeline(
        [
            ("obj", FunctionTransformer(_to_object, feature_names_out="one-to-one")),
            ("fill", SimpleImputer(strategy="constant", fill_value="Bilinmiyor")),
            (
                "ord",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=np.nan,
                    min_frequency=20,
                    max_categories=250,
                ),
            ),
        ]
    )
    num = FunctionTransformer(_to_float, feature_names_out="one-to-one")
    pre = ColumnTransformer([("num", num, NUM_COLS), ("cat", cat, CAT_COLS)]).set_output(
        transform="pandas"
    )
    reg = HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=1500,
        max_leaf_nodes=63,
        min_samples_leaf=40,
        categorical_features=[f"cat__{c}" for c in CAT_COLS],
        # Km artınca fiyat düşer, yıl artınca artar; kısıt eğriyi tutarlı tutar.
        monotonic_cst={"num__mileage": -1, "num__year": 1},
        early_stopping=False,
        random_state=RANDOM_STATE,
    )
    pipe = Pipeline([("pre", pre), ("reg", reg)])
    return TransformedTargetRegressor(regressor=pipe, func=np.log1p, inverse_func=np.expm1)


def make_final_model() -> TransformedTargetRegressor:
    """Seçilen model (train.py ve arayüz bunu kullanır)."""
    if BEST_MODEL == "big_hist_gb":
        return make_big_hist_gb()
    if BEST_MODEL == "random_forest":
        return make_random_forest(**BEST_PARAMS)
    return make_hist_gb(**BEST_PARAMS)
