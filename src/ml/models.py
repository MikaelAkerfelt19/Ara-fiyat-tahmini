"""Model kurucu fonksiyonlar. Hepsi ham (clean edilmiş) X alır, USD fiyat döndürür."""

import numpy as np
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src.ml.config import CAT_COLS, NUM_COLS, RANDOM_STATE

# notebooks/03_modelleme.ipynb içindeki RandomizedSearchCV sonucuna göre elle yazıldı.
# Tarih: 16 Kasım 2026. 5 katlı CV MAE: varsayılan 6028 -> ayarlı 5881 (USD).
BEST_MODEL = "hist_gb"
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


def _wrap(reg, scale: bool) -> TransformedTargetRegressor:
    """Ön işleme + modeli birleştirir ve fiyatı log ölçeğinde öğretir.

    Fiyat sağa çarpık olduğu için log1p ile öğrenilir; böylece model oransal hatayı
    küçültür ve pahalı birkaç araba eğitimi domine etmez. Tahmin expm1 ile dolara döner.
    Ön işleme pipeline içinde olduğundan CV'de sızıntı olmaz.
    """
    pipe = Pipeline([("pre", make_preprocessor(scale)), ("reg", reg)])
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
    return _wrap(HistGradientBoostingRegressor(random_state=RANDOM_STATE, **params), scale=False)


def make_final_model() -> TransformedTargetRegressor:
    """Arama sonucunda seçilen model ve parametreleri (train.py ve arayüz bunu kullanır)."""
    if BEST_MODEL == "random_forest":
        return make_random_forest(**BEST_PARAMS)
    return make_hist_gb(**BEST_PARAMS)
