# Servis Sözleşmesi

Bu belge arayüz (Streamlit) ile backend'in (DB + model) **nerede ve nasıl buluştuğunu** tanımlar. Arayüz yalnızca burada listelenen fonksiyonları çağırır. Backend de bu fonksiyonları burada yazdığı gibi sağlar.

**Değişiklik kuralı:** Bu belgede veya `src/core/` altında bir değişiklik iki kişinin onayıyla yapılır. Önce bu belge güncellenir, sonra kod.

> **Durum:** Veri alanları kesinleşti (16 Kasım 2026).

---

## 1. Veri sınıfları: `src/core/schemas.py`

```python
from dataclasses import asdict, dataclass


@dataclass
class CarInput:
    """Arayüzün formdan topladığı araç bilgisi. `mileage` KİLOMETRE cinsindendir."""

    brand: str
    model: str
    year: int
    mileage: int  # kilometre (km)
    fuel_type: str
    transmission: str
    # İsteğe bağlı alanlar; bilinmiyorsa None
    condition: str | None = None
    cylinders: int | None = None
    drive: str | None = None
    body_type: str | None = None
    title_status: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Prediction:
    """Servisin döndürdüğü tahmin. price, low ve high TL cinsindendir."""

    price: float  # TL
    low: float | None  # olası aralığın alt sınırı, TL (yoksa None)
    high: float | None  # olası aralığın üst sınırı, TL (yoksa None)
    model_version: str
    currency: str = "TRY"
    usd_try: float | None = None  # tahminde kullanılan USD/TRY kuru
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
| `predict(car: CarInput) -> Prediction` | Tahmin | "Fiyatı Tahmin Et" butonu | TL fiyat = USD tahmin x güncel TCMB USD/TRY kuru x taban katsayı x km çarpanı x (ağır hasarlıysa 0,65). Taban önceliği: marka+model, sonra segment (elektrik, premium, suv, ekonomik), sonra genel. Km çarpanı 120.000-140.000 km arasında 1'den üst sınıra doğrusal yükselir; üst sınır modelin kendi fiyat kırılmasından türetilir, böylece km arttıkça TL fiyat yükselmez. Ayrıca km zarfı uygulanır: 0 km'den aracın km'sine 20.000 km adımlı ızgarada fiyat hesaplanıp en küçüğü alınır (daha düşük km'li hal daha ucuz olamaz); ağır hasarlıda model "Temiz" fiyatlar, sonra tam x0,65 uygulanır. Ağır hasarlı: tapu durumu "Ağır hasarlı" veya "Ağır hasarlı (onarılmış)". Geçersiz girdide `ValueError`, model yoksa `ModelNotReadyError` fırlatır |
| `save_prediction(car: CarInput, pred: Prediction) -> None` | – | `predict`'ten hemen sonra | `predictions` tablosuna bir satır yazar |
| `get_history(limit: int = 20) -> list[dict]` | Son tahminler | "Son tahminler" bölümü | En yeni en üstte. Her sözlükte `created_at`, girdi alanları ve `price` bulunur |
| `get_model_info() -> dict` | Model bilgisi | "Model hakkında" bölümü | Anahtarlar: `model_name`, `version`, `trained_at`, `mae`, `rmse`, `r2`, `n_train`, `metrics_currency`. Model yoksa değerler `None` olur. Model metrikleri (`mae`, `rmse`) USD cinsindendir; `metrics_currency` bunu belirtir |

**Notlar:**
- Fiyatlar TL cinsindendir: TCMB günlük USD satış kuru × Türkiye piyasa katsayısı.
- Kilometre (`mileage`) km cinsindendir.
- Kategori değerleri (yakıt, vites, durum, çekiş, kasa, tapu durumu) Türkçe etiketlerdir.
- İsteğe bağlı alanlar (`condition`, `cylinders`, `drive`, `body_type`, `title_status`) `None` olabilir.
- `get_model_info()` sonucundaki `metrics_currency` anahtarı model metriklerinin USD olduğunu belirtir.

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
        "condition": ["Hasarlı", "Orta", "Sıfır", "Sıfır gibi", "Çok iyi", "İyi"],
        "drive": ["4x4", "Arkadan itiş", "Önden çekiş"],
        "body_type": ["Hatchback", "SUV", "Sedan", "Station wagon"],
        "title_status": ["Ağır hasarlı", "Ağır hasarlı (onarılmış)", "Temiz"],
    }


def get_models_for_brand(brand: str) -> list[str]:
    return _MODELS.get(brand, [])


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
```

## 6. Dosya yolları

| Ne | Yol | Repoda mı? |
|---|---|---|
| Ham veri | `data/raw/train_data_v2.csv`, `data/raw/test_data_v2.csv` | Hayır |
| Veritabanı | `data/cars.db` | Hayır |
| Model | `models/model.joblib` | Hayır (Releases'e eklenir) |
| Model bilgisi | `models/model_meta.json` | Hayır |
| Türkiye katsayıları | `models/localization.json` | Hayır (`python -m src.ml.train` üretir) |

## 7. Veritabanı tabloları

```sql
-- Temizlenmiş veri. pandas.to_sql ile oluşturulur; sütunlar DATA.md'deki "temiz ad"lardır.
-- cars (id, year, mileage, cylinders, brand, model, fuel_type, transmission,
--       condition, drive, body_type, title_status, price)
-- price: USD. mileage: km.

CREATE TABLE IF NOT EXISTS predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL,   -- ISO 8601, örn. 2026-10-20T14:05:00
    input_json      TEXT    NOT NULL,   -- CarInput.to_dict() JSON olarak
    predicted_price REAL    NOT NULL,   -- TL
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
| 16 Kasım 2026 | CarInput alanları veriye göre kesinleşti; fiyat TL, kilometre km | Kaan |
| 16 Kasım 2026 | Gerçek servis: TCMB kuru ve Türkiye piyasa katsayısı | Kaan |
| 16 Kasım 2026 | Yumuşak km çarpanı (band yerine), ağır hasar %35 indirimi; title_status etiketleri "Ağır hasarlı" / "Ağır hasarlı (onarılmış)" | Kaan |
| 16 Kasım 2026 | Monoton kısıtlı model (km −, yıl +), km zarfı ve ağır hasarın tam x0,65 uygulanması (`tl_price`) | Kaan |
