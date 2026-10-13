# Backend Görevleri: Veri, Veritabanı, Model, Servis

> Sorumlu: **Kaan Demir** · İlgili belgeler: [CONTRACT.md](CONTRACT.md), [EGITIM_REHBERI.md](EGITIM_REHBERI.md), [DATA.md](DATA.md), [MODEL.md](MODEL.md)

Her görev bir GitHub Issue olur (başlık örneği: `B6 — Baseline model`). Görevi bitirince kutuyu işaretle ve PR açıklamasına `Closes #<issue>` yaz.

## Genel bakış

| Kod | Görev | Hafta | Bağımlılık | Milestone |
|---|---|---|---|---|
| B0 | Repo kurulumu | 0 | – | – |
| B1 | Sözleşme ve sahte servis | 0 | B0 | M1 |
| B2 | Veriyi tanıma (Rehber Adım 1) | 1 | B0 | M1 |
| B3 | Temizlik (Adım 2) | 1 | B2 | M1 |
| B4 | EDA (Adım 3) | 1 | B3 | M1 |
| B5 | Veritabanı | 2 | B3 | M2 |
| B6 | Baseline (Adım 4–5) | 2 | B3 | M2 |
| B7 | İlk pipeline modeli (Adım 6) | 2 | B6 | M2 |
| B8 | Ağaç modelleri, CV, ayar (Adım 7–8) | 3 | B7 | M2 |
| B9 | Final model ve kayıt (Adım 9) | 3 | B5, B8 | M2 |
| B10a | Gerçek servis: seçenekler, aralıklar, geçmiş | 2 | B5 | M2 |
| B10b | Gerçek servis: tahmin, model bilgisi | 3 | B9 | M2 |
| B11 | Testler, yorumlama, Kaggle gönderimi (Adım 10–11) | 4 | B9 | M3 |

**Mentorluk görevlerin** (her hafta):
- [ ] Arkadaşının PR'larını 24 saat içinde incele. Sadece "onay" verme, en az bir somut yorum yaz.
- [ ] Pazar demosunda arayüz tarafındaki takılmaları çöz.
- [ ] Sözleşmede bir değişiklik gerekiyorsa önce `CONTRACT.md`'yi güncelle, sonra ona haber ver.

---

## B0: Repo kurulumu (Hafta 0, 9–11 Ekim)

> **Not:** Klasör iskeleti, sürümlerin sabitlenmesi ve B1'in tamamı Codex'e verildi (`docs/CODEX_GOREV.md`). Sende GitHub tarafındaki adımlar ve Codex'in PR'ını incelemek kalıyor.

- [ ] GitHub'da `car-price-prediction` reposunu aç. Arkadaşını **Settings → Collaborators** ile ekle.
- [ ] Bu planlama paketindeki dosyaları (`README.md`, `CONTRIBUTING.md`, `.gitignore`, `requirements.txt`, `docs/`) ilk commit olarak gönder.
- [ ] Klasör iskeletini oluştur (`docs/PLAN.md` §5): boş `__init__.py` dosyaları, `models/.gitkeep`, `notebooks/`, `tests/`, `docs/img/`.
- [ ] `python -m venv .venv` → `pip install -r requirements.txt` → `pip freeze` ile `requirements.txt` sürümlerini sabitle.
- [ ] `main` için PR zorunluluğunu aç (`CONTRIBUTING.md` §2).
- [ ] **Projects** panosu, etiketler ve milestone'lar (`CONTRIBUTING.md` §6).
- [ ] `GOREVLER_BACKEND.md` ve `ARAYUZ_KONSEPT.md` §9 içindeki her görev için bir issue aç.

**Kabul kriteri:** Arkadaşın repoyu klonlayıp `pip install -r requirements.txt` komutunu hatasız çalıştırabiliyor.

**Commit:** `chore: proje iskeleti ve planlama belgeleri`

---

## B1: Sözleşme ve sahte servis (Hafta 0)

Arkadaşın pazartesi işe başlayabilsin diye **hafta sonu bitmeli.**

- [ ] `src/core/schemas.py`, `errors.py`, `api.py`, `mock_service.py` dosyalarını `CONTRACT.md` §1–5'teki kodla oluştur.
- [ ] En basit `app.py` dosyasını oluştur (sadece `st.title`). Arkadaşın A1'de bunun üzerine inşa edecek.

**Kabul kriteri:**
```bash
# macOS/Linux
USE_MOCK=1 python -c "from src.core.api import service; print(service.get_options())"
```
Komut sahte seçenekleri yazdırıyor ve `USE_MOCK=1 streamlit run app.py` boş bir sayfa açıyor.

**Commit:** `feat(core): servis sözleşmesi ve sahte servis`

---

## B2: Veriyi tanıma (Hafta 1)

→ [EGITIM_REHBERI.md](EGITIM_REHBERI.md) **Adım 0–1**

- [ ] `notebooks/01_tanima.ipynb`
- [ ] `DATA.md` §1–4 dolduruldu
- [ ] **Kontrol noktası 1** yapıldı: `NUM_COLS`, `CAT_COLS` ve `CarInput` alanları kesinleşti
- [ ] `CONTRACT.md`, `schemas.py` ve `mock_service.py` yeni alanlara göre güncellendi; arkadaşına haber verildi (formdaki alanlar buna göre değişecek)

---

## B3: Temizlik (Hafta 1)

→ Rehber **Adım 2**

- [ ] `src/ml/config.py`, `src/ml/preprocess.py`
- [ ] `tests/test_preprocess.py` geçiyor
- [ ] `DATA.md` §5–6 (kararlar ve gerekçeleri)

---

## B4: EDA (Hafta 1)

→ Rehber **Adım 3**

- [ ] `notebooks/02_eda.ipynb`, rapor için en az 4 grafik `docs/img/` altında
- [ ] **Kontrol noktası 2** yapıldı, `DATA.md` §7 dolu

---

## B5: Veritabanı (Hafta 2)

**Amaç:** Temizlenmiş veriyi ve uygulama verilerini (tahminler, model kayıtları) SQLite'ta tutmak.

**Tasarım notları:**
- Her fonksiyon kendi bağlantısını açıp kapatır (`contextlib.closing`). Streamlit kodu farklı thread'lerde çalıştırabildiği için tek bir global bağlantı "SQLite objects created in a thread…" hatası verir.
- Sorgularda **kullanıcıdan gelen değerler** (marka adı vb.) her zaman `?` parametresiyle verilir. Asla f-string ile SQL'e yazılmaz. Sütun adları ise yalnızca `config.py`'den gelir.

`src/db/schema.py`

```python
import sqlite3
from pathlib import Path

DB_PATH = Path("data/cars.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL,
    input_json      TEXT    NOT NULL,
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
    is_active   INTEGER NOT NULL DEFAULT 0
);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
```

`src/db/load_data.py`

```python
"""Ham CSV'yi temizleyip cars tablosuna yükler. Çalıştırma: python -m src.db.load_data"""

from contextlib import closing

import pandas as pd

from src.db.schema import connect, create_tables
from src.ml.preprocess import clean, filter_train_rows

RAW_PATH = "data/raw/train.csv"


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    df = filter_train_rows(clean(raw))
    with closing(connect()) as conn:
        create_tables(conn)
        df.to_sql("cars", conn, if_exists="replace", index=False)  # tekrar çalıştırılabilir
        conn.commit()
    print(f"cars tablosu yazıldı: {len(df)} satır ({len(raw) - len(df)} satır elendi)")


if __name__ == "__main__":
    main()
```

`src/db/queries.py`

```python
"""Veritabanı sorguları. Servis katmanı ve train.py bunları kullanır."""

import json
from contextlib import closing
from datetime import datetime

import pandas as pd

from src.db.schema import connect


def load_cars() -> pd.DataFrame:
    with closing(connect()) as conn:
        return pd.read_sql("SELECT * FROM cars", conn)


def distinct_values(columns: list[str]) -> dict[str, list[str]]:
    # Sütun adları yalnızca config.py'den gelir, kullanıcıdan değil.
    out = {}
    with closing(connect()) as conn:
        for col in columns:
            rows = conn.execute(
                f'SELECT DISTINCT "{col}" FROM cars WHERE "{col}" IS NOT NULL ORDER BY 1'
            ).fetchall()
            out[col] = [r[0] for r in rows]
    return out


def models_for_brand(brand: str) -> list[str]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT DISTINCT model FROM cars WHERE brand = ? AND model IS NOT NULL ORDER BY 1",
            (brand,),
        ).fetchall()
    return [r[0] for r in rows]


def numeric_ranges(columns: list[str]) -> dict[str, tuple[float, float]]:
    cols = ", ".join(f'"{c}"' for c in columns)
    with closing(connect()) as conn:
        df = pd.read_sql(f"SELECT {cols} FROM cars", conn)
    return {c: (float(df[c].quantile(0.01)), float(df[c].quantile(0.99))) for c in columns}


def insert_prediction(inputs: dict, price: float, model_version: str) -> None:
    with closing(connect()) as conn:
        conn.execute(
            "INSERT INTO predictions (created_at, input_json, predicted_price, model_version) "
            "VALUES (?, ?, ?, ?)",
            (
                datetime.now().isoformat(timespec="seconds"),
                json.dumps(inputs, ensure_ascii=False),
                price,
                model_version,
            ),
        )
        conn.commit()


def recent_predictions(limit: int = 20) -> list[dict]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT created_at, input_json, predicted_price FROM predictions "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {"created_at": created, **json.loads(inputs), "price": round(price)}
        for created, inputs, price in rows
    ]


def insert_model_run(meta: dict, params: dict) -> None:
    with closing(connect()) as conn:
        conn.execute("UPDATE model_runs SET is_active = 0")
        conn.execute(
            "INSERT INTO model_runs (created_at, model_name, version, params_json, n_train, "
            "mae, rmse, r2, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (
                meta["trained_at"],
                meta["model_name"],
                meta["version"],
                json.dumps(params, default=str),
                meta["n_train"],
                meta["mae"],
                meta["rmse"],
                meta["r2"],
            ),
        )
        conn.commit()
```

Sütun adları (`brand`, `model`) şimdilik yer tutucudur. B2'den sonra `DATA.md`'deki temiz adlara göre güncellenir.

- [ ] `python -m src.db.load_data` çalışıyor ve iki kez çalıştırınca da hata vermiyor
- [ ] `tests/test_queries.py`: geçici bir veritabanıyla `insert_prediction` → `recent_predictions` akışı test ediliyor (`monkeypatch` ile `DB_PATH`'i `tmp_path` altına yönlendir)

**Commit:** `feat(db): sqlite şeması, veri yükleme ve sorgular`

---

## B6–B9: Model

→ Rehber **Adım 4–9**. Her adımın sonunda `MODEL.md` deney tablosuna bir satır ekle.

- [ ] B6: `src/ml/evaluate.py`, baseline (`MODEL.md` satır 0)
- [ ] B7: `src/ml/models.py` içinde `make_linear_model` · **Kontrol noktası 3**
- [ ] B8: `make_random_forest`, `make_hist_gb`, CV, `BEST_PARAMS`, `make_final_model` · **Kontrol noktası 4**
- [ ] B9: `src/ml/train.py` · **Kontrol noktası 5**

---

## B10: Gerçek servis

`src/core/service.py`. İmzalar `mock_service.py` ile **birebir aynı.**

```python
"""Gerçek servis. Fonksiyon imzaları docs/CONTRACT.md ile aynıdır."""

import json
import math
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from src.core.errors import ModelNotReadyError
from src.core.schemas import CarInput, Prediction
from src.db import queries
from src.ml.config import CAT_COLS, NUM_COLS

MODEL_PATH = Path("models/model.joblib")
META_PATH = Path("models/model_meta.json")


# ---------- B10a (Hafta 2): veritabanından gelenler ----------


def get_options() -> dict[str, list[str]]:
    return queries.distinct_values([c for c in CAT_COLS if c != "model"])


def get_models_for_brand(brand: str) -> list[str]:
    return queries.models_for_brand(brand)


def get_ranges() -> dict[str, tuple[float, float]]:
    return queries.numeric_ranges(NUM_COLS)


def save_prediction(car: CarInput, pred: Prediction) -> None:
    queries.insert_prediction(car.to_dict(), pred.price, pred.model_version)


def get_history(limit: int = 20) -> list[dict]:
    return queries.recent_predictions(limit)


# ---------- B10b (Hafta 3): model ----------


@lru_cache(maxsize=1)  # model bir kez yüklenir; yeni model için Streamlit'i yeniden başlat
def _load_model():
    if not MODEL_PATH.exists() or not META_PATH.exists():
        raise ModelNotReadyError("Model bulunamadı. Önce: python -m src.ml.train")
    model = joblib.load(MODEL_PATH)
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    return model, meta


def _validate(car: CarInput) -> None:
    if car.mileage < 0:
        raise ValueError("Kilometre negatif olamaz.")
    low, high = get_ranges()["year"]
    if not low <= car.year <= high:
        raise ValueError(f"Model yılı {int(low)}–{int(high)} aralığında olmalı.")


def predict(car: CarInput) -> Prediction:
    _validate(car)
    model, meta = _load_model()
    X = pd.DataFrame([car.to_dict()])[meta["features"]]
    price = float(model.predict(X)[0])
    q_low, q_high = meta["interval_log_quantiles"]
    return Prediction(
        price=price,
        low=price * math.exp(q_low),
        high=price * math.exp(q_high),
        model_version=meta["version"],
    )


def get_model_info() -> dict:
    keys = ["model_name", "version", "trained_at", "mae", "rmse", "r2", "n_train"]
    try:
        _, meta = _load_model()
    except ModelNotReadyError:
        return dict.fromkeys(keys)
    return {k: meta.get(k) for k in keys}
```

- [ ] **B10a (Hafta 2):** Veritabanı fonksiyonları çalışıyor. Arkadaşın `USE_MOCK=0` ile seçenekleri gerçek veriden görebiliyor (bu aşamada `predict` henüz hata verebilir).
- [ ] **B10b (Hafta 3):** `predict` ve `get_model_info` çalışıyor.
- [ ] `tests/test_service.py`: Model varken `predict` pozitif bir fiyat ve `low <= price <= high` döndürüyor. Negatif kilometrede `ValueError` fırlatıyor.

**Kabul kriteri (M2):**
```bash
python -m src.db.load_data && python -m src.ml.train && streamlit run app.py
```
Formdan gerçek tahmin geliyor ve "Son tahminler" bölümünde görünüyor.

**Commit:** `feat(core): gerçek servis katmanı`

---

## B11: Kapanış (Hafta 4)

- [ ] Rehber **Adım 10**: özellik önemi ve hata analizi → `MODEL.md` §4–5
- [ ] Rehber **Adım 11** (bonus): Kaggle gönderimi → `MODEL.md` §6
- [ ] `pytest` ve `ruff check .` temiz
- [ ] Final model GitHub **Releases** → `v1.0` altına `model.joblib` ve `model_meta.json` olarak eklendi; README'ye indirme notu yazıldı
- [ ] Sunumdaki backend slaytları: veri, temizlik kararları, model karşılaştırması, özellik önemi
