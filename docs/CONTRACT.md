# Servis Sözleşmesi

Bu belge arayüz (Streamlit) ile backend'in (DB + model) **nerede ve nasıl buluştuğunu** tanımlar. Arayüz yalnızca burada listelenen fonksiyonları çağırır. Backend de bu fonksiyonları burada yazdığı gibi sağlar.

**Değişiklik kuralı:** Bu belgede veya `src/core/` altında bir değişiklik iki kişinin onayıyla yapılır. Önce bu belge güncellenir, sonra kod.

> **Durum:** Taslak. `CarInput` alanları, veri setinin sütunları görüldükten sonra (Rehber Adım 1, `DATA.md`) kesinleşecek. Aşağıdaki alanlar şimdilik yer tutucu.

---

## 1. Veri sınıfları: `src/core/schemas.py`

```python
from dataclasses import asdict, dataclass


@dataclass
class CarInput:
    """Arayüzün formdan topladığı araç bilgisi."""

    brand: str
    model: str
    year: int
    mileage: int
    fuel_type: str
    transmission: str
    # TODO(Hafta 1): DATA.md kesinleşince veri setindeki sütunlara göre güncelle

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Prediction:
    """Servisin döndürdüğü tahmin."""

    price: float
    low: float | None  # olası aralığın alt sınırı (yoksa None)
    high: float | None  # olası aralığın üst sınırı (yoksa None)
    model_version: str
```

**Kural:** `CarInput` alan adları, `cars` tablosundaki ve modelin beklediği sütun adlarıyla **birebir aynıdır**. Böylece `pd.DataFrame([car.to_dict()])` doğrudan modele verilebilir.

## 2. Hatalar: `src/core/errors.py`

```python
class ModelNotReadyError(Exception):
    """Model dosyası henüz yok veya yüklenemedi."""
```

Geçersiz girdi için Python'un kendi `ValueError` sınıfı kullanılır.

## 3. Servis fonksiyonları

Arayüz bunları `from src.core.api import service` ile alır ve `service.predict(...)` şeklinde çağırır.

| Fonksiyon | Döndürür | Arayüzde nerede | Davranış |
|---|---|---|---|
| `get_options() -> dict[str, list[str]]` | Alan adı → seçenekler | Açılır listeler (marka, yakıt, vites…) | Değerler alfabetik sıralı ve tekrarsızdır. `model` alanı **yoktur**, o markaya bağlıdır |
| `get_models_for_brand(brand: str) -> list[str]` | Model adları | Marka seçilince model listesi | Bilinmeyen marka için `[]` döner |
| `get_ranges() -> dict[str, tuple[float, float]]` | Alan adı → (min, max) | Sayı kutularının sınırları | Verinin %1 ve %99 yüzdeliklerinden hesaplanır |
| `predict(car: CarInput) -> Prediction` | Tahmin | "Fiyatı Tahmin Et" butonu | Geçersiz girdide `ValueError`, model yoksa `ModelNotReadyError` fırlatır |
| `save_prediction(car: CarInput, pred: Prediction) -> None` | – | `predict`'ten hemen sonra | `predictions` tablosuna bir satır yazar |
| `get_history(limit: int = 20) -> list[dict]` | Son tahminler | "Son tahminler" bölümü | En yeni en üstte. Her sözlükte `created_at`, girdi alanları ve `price` bulunur |
| `get_model_info() -> dict` | Model bilgisi | "Model hakkında" bölümü | Anahtarlar: `model_name`, `version`, `trained_at`, `mae`, `rmse`, `r2`, `n_train`. Model yoksa değerler `None` olur |

## 4. Mock ve gerçek servis seçimi: `src/core/api.py`

```python
import os

if os.getenv("USE_MOCK", "0") == "1":
    from src.core import mock_service as service
else:
    from src.core import service

__all__ = ["service"]
```

- M2'ye kadar arayüz `USE_MOCK=1` ile çalışır.
- `mock_service.py` ve `service.py` **aynı fonksiyon adlarına ve imzalara** sahiptir.

## 5. Sahte servis: `src/core/mock_service.py`

Kaan bunu Hafta 0'da yazar. Arkadaş Hafta 1'den itibaren bunu kullanarak arayüzü geliştirir.

```python
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
```

## 6. Dosya yolları

| Ne | Yol | Repoda mı? |
|---|---|---|
| Ham veri | `data/raw/train.csv`, `data/raw/test.csv` | Hayır |
| Veritabanı | `data/cars.db` | Hayır |
| Model | `models/model.joblib` | Hayır (Releases'e eklenir) |
| Model bilgisi | `models/model_meta.json` | Hayır |

## 7. Veritabanı tabloları

```sql
-- Temizlenmiş veri. pandas.to_sql ile oluşturulur; sütunlar DATA.md'deki "temiz ad"lardır.
-- cars (...)

CREATE TABLE IF NOT EXISTS predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL,   -- ISO 8601, örn. 2026-10-20T14:05:00
    input_json      TEXT    NOT NULL,   -- CarInput.to_dict() JSON olarak
    predicted_price REAL    NOT NULL,
    model_version   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS model_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL,
    model_name  TEXT    NOT NULL,
    version     TEXT    NOT NULL,
    params_json TEXT,
    n_train     INTEGER,
    mae         REAL,
    rmse        REAL,
    r2          REAL,
    is_active   INTEGER NOT NULL DEFAULT 0  -- arayüzde kullanılan model 1
);
```

`input_json` sütunu bilerek JSON tutuluyor. `CarInput`'a alan eklendiğinde tabloyu değiştirmek gerekmez.

## 8. Değişiklik günlüğü

| Tarih | Değişiklik | Onaylayan |
|---|---|---|
| 9 Ekim 2026 | İlk taslak | Kaan |
