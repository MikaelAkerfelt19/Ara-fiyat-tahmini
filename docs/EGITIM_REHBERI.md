# Model Eğitimi Rehberi (Sıfırdan)

> Kimin için: Kaan (daha önce model eğitmemiş, Python bilen biri) · Kapsam: Hafta 1–4 · İlgili görevler: B2–B4, B6–B9, B11

## Bu rehber nasıl kullanılır?

Her adım aynı düzende ilerler:

1. **Amaç:** Bu adımın sonunda elinde ne olacak?
2. **Kavram:** Yapacağın şeyin arkasındaki fikir, kısaca.
3. **Yap:** Kod. Önce notebook'ta dene, çalışınca `src/ml/` altına taşı.
4. **Kontrol et:** Doğru yaptığını nereden anlarsın?
5. **Kontrol noktası** (bazı adımlarda): Çıktıyı sohbete getir, birlikte yorumlayalım, sonra devam et.
6. **Commit:** Adımı bitirince ne commit'leyeceğin.

**Öğrenme kuralı:** Bu kısmı öğrenmek istiyorsun, o yüzden kodu kendin yaz ve satır satır çalıştır. Kodu yapay zekâya toptan yazdırma. Bir satırı anlamadığında "bu ne yapıyor?" diye sor. Sunumda hoca "bu satır ne işe yarıyor?" diye sorabilir.

**Notebook mu, `.py` dosyası mı?** Keşif ve deneme notebook'ta yapılır (`notebooks/`). Kalıcı ve tekrar çalıştırılacak kod `src/ml/` altına taşınır. Arayüz ve `train.py` yalnızca `src/` altındaki kodu kullanır.

---

## Büyük resim

Makine öğrenmesi burada şunu yapar: geçmiş ilanlara bakarak bir **fonksiyon öğrenir**:

```
f(marka, model, yıl, kilometre, yakıt, vites, ...)  ≈  fiyat
```

**Eğitmek**, bu fonksiyonun ayarlarını, fiyatı bilinen ilanlardaki hatayı en aza indirecek şekilde bulmaktır. Sonra fonksiyon, fiyatını hiç görmediği bir araç için tahmin yapar.

```
train.csv ─► temizle ─► böl ─┬─► eğitim seti (%80) ─► model.fit(X, y)       "öğren"
                             │
                             └─► doğrulama seti (%20) ─► model.predict(X) ─► gerçekle karşılaştır
                                                                             "sınav"
```

### Sözlük

| Terim | Anlamı | Bu projede |
|---|---|---|
| Özellik (feature), `X` | Modele verilen girdi sütunları | marka, yıl, kilometre… |
| Hedef (target), `y` | Tahmin edilen sütun | fiyat |
| Eğitim seti | Modelin öğrendiği veri | `train.csv` verisinin %80'i |
| Doğrulama seti | Modelin hiç görmediği "sınav" verisi | `train.csv` verisinin %20'si |
| Baseline | En basit tahmin, geçilmesi gereken çizgi | Herkese medyan fiyatı söylemek |
| Aşırı öğrenme (overfitting) | Eğitim verisini ezberleyip yeni veride kötü olmak | Eğitim hatası, doğrulama hatasından çok küçük |
| Veri sızıntısı (leakage) | Sınav verisinden bilginin eğitime karışması; sonuç sahte şekilde iyi çıkar | Kendi kendini kandırmak |
| One-hot encoding | Kategorik değeri 0/1 sütunlarına çevirmek | yakıt=Dizel → `[0, 1, 0, 0]` |
| Pipeline | Ön işleme ve modeli tek nesnede birleştirmek | Arayüzden gelen ham veri doğrudan modele girer |
| Hiperparametre | Modelin senin seçtiğin ayarları | ağaç sayısı, öğrenme hızı |
| Çapraz doğrulama (CV) | Veriyi k parçaya bölüp k kez eğitip ölçmek | 5 kat |

### Metrikler: "ne kadar iyiyiz?"

| Metrik | Anlamı | Nasıl okunur |
|---|---|---|
| **MAE** (ana metrik) | Tahminler ortalama kaç para birimi şaşıyor | "Ortalama 2.300 $ yanılıyoruz." Küçük olan iyi |
| RMSE | MAE'ye benzer, ama büyük hataları daha çok cezalandırır | RMSE, MAE'den çok büyükse bazı tahminler çok kötü demektir |
| R² | Fiyattaki değişkenliğin ne kadarını açıklıyoruz | 1 mükemmel, 0 "herkese ortalamayı söylemek" kadar. 0,8–0,9 bu tür veride iyidir |

---

## Adım 0: Ortam

**Amaç:** Notebook açıp `src` modüllerini içe aktarabilmek.

**Yap:**
1. `README.md`'deki kurulumu yap (venv, `pip install -r requirements.txt`).
2. VS Code'da Python ve Jupyter eklentilerini kur. Notebook çekirdeği (kernel) olarak `.venv`'i seç.
3. Veriyi `data/raw/` içine indir (README → "Veriyi indirme").
4. Her notebook'un **ilk hücresi** şu olsun:

```python
import os
import sys

if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")  # repo köküne geç; data/ ve src/ yolları buna göre çalışır
sys.path.insert(0, os.getcwd())  # "from src.ml ..." içe aktarmaları çalışsın
```

**Kontrol et:** `os.listdir("data/raw")` çıktısında `train.csv` görünüyor.

---

## Adım 1: Veriyi tanı (B2)

**Amaç:** Verinin neye benzediğini bilmek ve `DATA.md`'nin ilk halini doldurmak.

**Kavram:** Model yazmadan önce veriye bakılır. Hangi sütunlar var, hangisi sayı, hangisi kategori, ne kadar eksik var, sayı gibi görünen ama metin olan sütun var mı? Bu adımı atlayan herkes 3. adımda geri döner.

**Yap:** `notebooks/01_tanima.ipynb`

```python
import pandas as pd

pd.set_option("display.max_columns", None)

df = pd.read_csv("data/raw/train.csv")
print(df.shape)  # (satır, sütun)
df.head()
```

```python
df.info()  # sütun türleri ve eksik olmayan değer sayıları
```

```python
df.describe(include="all").T  # her sütun için özet
```

```python
df.isna().mean().sort_values(ascending=False)  # eksik oranı
```

```python
df.nunique().sort_values()  # her sütunda kaç farklı değer var
```

```python
# Sayısal olmayan (metin) sütunlardan örnek değerler
for col in df.select_dtypes(exclude="number").columns:
    print(f"{col:20s}", df[col].unique()[:8])
```

**Cevaplaman gereken sorular** (`DATA.md` §2–4):
- [ ] Hedef sütun hangisi? Para birimi ne?
- [ ] Hangi sütunlar sayı olmalı ama `object` veya `str` (metin) türünde görünüyor? Örnek: `"120,000 km"`, `"2.0 Turbo"`
- [ ] Hangi sütunlarda eksik değer var, oranı ne?
- [ ] Hangi kategorik sütunlarda çok fazla farklı değer var? (Örn. yüzlerce model adı)
- [ ] Tahminde işe yaramayacak sütun var mı? (ID gibi)
- [ ] Kaggle'da **Overview → Evaluation** bölümünde değerlendirme metriği ne?

> **Kontrol noktası 1:** `df.shape`, `df.head()`, `df.info()`, eksik oranları ve metin sütunu örneklerinin çıktısını sohbete yapıştır. Birlikte şunları yapacağız: `DATA.md` sözlüğünü dolduracağız, temizlik kararlarını vereceğiz, `NUM_COLS` / `CAT_COLS` listelerini ve `CarInput` alanlarını kesinleştireceğiz (bu yüzden `CONTRACT.md` de güncellenecek).

**Commit:** `feat(ml): veri tanıma notebook'u ekle` · `docs: DATA.md ilk veri sözlüğü`

---

## Adım 2: Temizle (B3)

**Amaç:** Ham veriyi, modelin anlayacağı türlere çeviren tek bir yerin olması.

**Kavram:** Modeller yalnızca sayılarla çalışır. `"120,000 km"` bir metindir; önce `120000` sayısına çevrilmesi gerekir. `"-"` gibi işaretler aslında "eksik" anlamına gelir. Bunların yanında tekrar eden satırlar ve saçma fiyatlar (1 $ veya 10 milyon $) modeli bozar.

**Altın kural: iki ayrı fonksiyon yaz.**

| Fonksiyon | Ne yapar | Nerede kullanılır |
|---|---|---|
| `clean(df)` | Sütun adlarını düzeltir, türleri çevirir. **Satır silmez.** | Eğitimde, `test.csv` tahmininde, gerekirse arayüzde |
| `filter_train_rows(df)` | Tekrar eden ve uç değerli satırları siler | **Yalnızca eğitim verisinde** |

Neden ayrı? `test.csv` içindeki her satır için tahmin vermek zorundasın; oradan satır silersen Kaggle gönderimi bozulur. Arayüzde de kullanıcının girdiğini "silemezsin".

**Yap:** `src/ml/config.py` (sütun listeleri Adım 1'den sonra kesinleşecek)

```python
"""Model için ortak sabitler. Sütun adları DATA.md'deki "temiz ad"lardır."""

TARGET = "price"
NUM_COLS = ["year", "mileage"]  # TODO: Adım 1 sonrası güncelle
CAT_COLS = ["brand", "model", "fuel_type", "transmission"]  # TODO: Adım 1 sonrası güncelle
FEATURES = NUM_COLS + CAT_COLS
RANDOM_STATE = 42
```

`src/ml/preprocess.py`

```python
"""Ham veriyi temizleme. Kararların gerekçeleri docs/DATA.md içinde."""

import numpy as np
import pandas as pd

from src.ml.config import TARGET


def _clean_name(name: str) -> str:
    return name.strip().lower().replace(".", "").replace(" ", "_")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Tür düzeltmeleri. SATIR SİLMEZ: eğitim, test ve tahmin anında kullanılır."""
    df = df.copy()
    df.columns = [_clean_name(c) for c in df.columns]

    # Eksik anlamına gelen işaretleri gerçek eksiğe çevir
    df = df.replace({"-": np.nan, "": np.nan})

    # --- Adım 1'deki bulgulara göre doldurulacak örnekler ---
    # "120,000 km" → 120000
    # df["mileage"] = pd.to_numeric(
    #     df["mileage"].astype(str).str.replace(r"[^\d]", "", regex=True), errors="coerce"
    # )
    # "2.0 Turbo" → engine_volume=2.0, turbo=1
    # df["turbo"] = df["engine_volume"].astype(str).str.contains("Turbo").astype(int)
    # df["engine_volume"] = pd.to_numeric(
    #     df["engine_volume"].astype(str).str.extract(r"([\d.]+)")[0], errors="coerce"
    # )
    return df


def filter_train_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Yalnızca EĞİTİM verisi için: tekrarları ve uç fiyatları atar."""
    df = df.drop_duplicates()
    low, high = df[TARGET].quantile([0.005, 0.995])
    return df[df[TARGET].between(low, high)]
```

`tests/test_preprocess.py`

```python
import pandas as pd

from src.ml.preprocess import clean


def test_clean_satir_silmez():
    df = pd.DataFrame({"Prod. year": [2010, 2015], "Fuel type": ["Petrol", "-"]})
    assert len(clean(df)) == len(df)


def test_clean_sutun_adlarini_duzeltir():
    df = pd.DataFrame({"Prod. year": [2010], "Fuel type": ["Petrol"]})
    assert list(clean(df).columns) == ["prod_year", "fuel_type"]


def test_clean_tire_isaretini_eksige_cevirir():
    df = pd.DataFrame({"Fuel type": ["Petrol", "-"]})
    assert clean(df)["fuel_type"].isna().sum() == 1
```

**Kontrol et:**
- `clean(df).info()` çıktısında sayı olması gereken her sütun `int64` veya `float64`.
- `len(clean(df)) == len(df)`
- `pytest` geçiyor.
- `DATA.md` §5–6'ya her kararı gerekçesiyle yazdın.

**Commit:** `feat(ml): clean ve filter_train_rows fonksiyonları` · `test(ml): temizlik testleri`

---

## Adım 3: Keşifsel veri analizi, EDA (B4)

**Amaç:** Fiyatı neyin etkilediğine dair sezgi kazanmak ve rapor için grafik üretmek.

**Kavram:** EDA'da modelin ne öğrenebileceğine önceden bakarsın. Yaş arttıkça fiyat düşüyor mu? Kilometre ile ilişki nasıl? Bazı markalar belirgin şekilde pahalı mı? Fiyat dağılımı çok çarpıksa (çoğu ucuz, az sayıda çok pahalı araç), logaritma almak modeli rahatlatır.

**Yap:** `notebooks/02_eda.ipynb`

```python
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.ml.preprocess import clean, filter_train_rows

df = filter_train_rows(clean(pd.read_csv("data/raw/train.csv")))
```

```python
# 1) Fiyat dağılımı: ham ve log
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
df["price"].plot.hist(bins=60, ax=ax[0], title="Fiyat")
np.log1p(df["price"]).plot.hist(bins=60, ax=ax[1], title="log(1 + fiyat)")
plt.tight_layout()
```

```python
# 2) Yıl ve kilometre ile fiyat (log ölçekli y ekseni)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
df.plot.scatter(x="year", y="price", alpha=0.15, logy=True, ax=ax[0])
df.plot.scatter(x="mileage", y="price", alpha=0.15, logy=True, ax=ax[1])
plt.tight_layout()
```

```python
# 3) En sık 20 marka ve medyan fiyatları
fig, ax = plt.subplots(1, 2, figsize=(11, 5))
df["brand"].value_counts().head(20).sort_values().plot.barh(ax=ax[0], title="İlan sayısı")
top = df["brand"].value_counts().head(20).index
df[df["brand"].isin(top)].groupby("brand")["price"].median().sort_values().plot.barh(
    ax=ax[1], title="Medyan fiyat"
)
plt.tight_layout()
```

```python
# 4) Sayısal sütunların fiyatla korelasyonu
df.select_dtypes("number").corr()["price"].sort_values()
```

Rapor için grafikleri kaydet: `plt.savefig("docs/img/fiyat_dagilimi.png", dpi=150, bbox_inches="tight")`

**Neye bakacaksın?**
- Log alınmış fiyat histogramı daha "çan eğrisi" gibi mi? Öyleyse Adım 6'da log hedef kullanacağız.
- Yıl ve kilometre ile fiyat arasında net bir eğilim var mı?
- Grafikte saçma görünen noktalar var mı? (Örn. 2024 model, 900.000 km.) Varsa temizlik kararlarına geri dön.

> **Kontrol noktası 2:** Grafikleri (veya ekran görüntüsünü) ve korelasyon çıktısını getir. Birlikte yorumlayıp `DATA.md` §7'ye 4–6 madde yazacağız.

**Commit:** `feat(ml): EDA notebook'u ve grafikler`

---

## Adım 4: Veriyi böl

**Amaç:** Modeli dürüstçe ölçebileceğin bir "sınav" setinin olması.

**Kavram:** Modeli öğrendiği veride ölçersen kendini kandırırsın, çünkü ezberlemiş olabilir. `test.csv` dosyasında fiyat yok, o yüzden `train.csv`'nin %20'sini kenara ayırıp **hiç eğitimde kullanmıyoruz**. `random_state=42` her çalıştırmada aynı bölmeyi sağlar; sonuçlar karşılaştırılabilir olur.

**Veri sızıntısı uyarısı:** Ortalama, en sık değer, one-hot sütunları gibi her şey yalnızca eğitim setinden öğrenilmeli. Adım 6'daki `Pipeline` bunu senin yerine otomatik yapar. Bu yüzden ön işlemeyi elle, bölmeden önce tüm veriye **uygulama**. (`clean()` serbest, çünkü veriden bir şey öğrenmiyor, sadece tür çeviriyor.)

**Yap:** `notebooks/03_modelleme.ipynb`

```python
import pandas as pd
from sklearn.model_selection import train_test_split

from src.ml.config import FEATURES, RANDOM_STATE, TARGET
from src.ml.preprocess import clean, filter_train_rows

df = filter_train_rows(clean(pd.read_csv("data/raw/train.csv")))
X, y = df[FEATURES], df[TARGET]

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)
print(len(X_train), len(X_val))
```

**Kontrol et:** Satır sayıları yaklaşık %80 / %20.

> **İpucu:** Veri çok büyükse ve denemeler yavaşsa, deneme sırasında `df = df.sample(20_000, random_state=RANDOM_STATE)` ile küçült. Final eğitimde (Adım 9) tüm veriyi kullan.

---

## Adım 5: Baseline (B6)

**Amaç:** "İyi" kelimesine bir anlam vermek.

**Kavram:** Hiçbir şey öğrenmeyen bir model düşün: her araba için eğitim setindeki **medyan fiyatı** söyler. Bunun MAE'si, geçilmesi gereken çizgidir. Bundan kötü bir model işe yaramaz.

**Yap:** `src/ml/evaluate.py`

```python
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error


def evaluate(model, X, y) -> dict[str, float]:
    pred = model.predict(X)
    return {
        "mae": mean_absolute_error(y, pred),
        "rmse": root_mean_squared_error(y, pred),
        "r2": r2_score(y, pred),
    }
```

Notebook'ta:

```python
from sklearn.dummy import DummyRegressor

from src.ml.evaluate import evaluate

baseline = DummyRegressor(strategy="median").fit(X_train, y_train)
evaluate(baseline, X_val, y_val)
```

**Kontrol et:** R² sıfıra yakın veya biraz negatif. Bu normal, çünkü model hiçbir şey öğrenmiyor. MAE'yi `MODEL.md`'de 0 numaralı satıra yaz.

**Commit:** `feat(ml): evaluate fonksiyonu ve medyan baseline`

---

## Adım 6: İlk gerçek model (B7)

**Amaç:** Baseline'ı geçen, baştan sona doğru kurulmuş ilk model.

**Kavram:** Üç parçayı birleştiriyoruz:

1. **Ön işleme (`ColumnTransformer`):** Sayısal sütunlarda eksikleri medyanla doldur ve ölçekle. Kategorik sütunlarda eksikleri en sık değerle doldur ve one-hot'a çevir. Çok seyrek kategoriler (20'den az görülen) tek bir "seyrek" grupta birleşir; eğitimde hiç görülmemiş bir kategori gelirse hata vermez.
2. **Model (`Ridge`):** Doğrusal regresyon. Her özelliğe bir ağırlık verir. Basit, hızlı ve yorumlanabilir.
3. **Log hedef (`TransformedTargetRegressor`):** Model `log(1 + fiyat)` tahmin etmeyi öğrenir, sonuç otomatik olarak fiyata geri çevrilir. Böylece 5.000 $'lık arabada 1.000 $ hata ile 100.000 $'lık arabada 1.000 $ hata aynı ağırlıkta sayılmaz; model **oransal** hatayı küçültmeye çalışır.

Hepsi tek bir nesnede olduğu için `model.fit(X_train, y_train)` dediğinde ön işleme yalnızca eğitim setinden öğrenilir (sızıntı yok). Arayüzden gelen ham bir satır da `model.predict()`'e doğrudan verilebilir.

**Yap:** `src/ml/models.py`

```python
"""Model kurucu fonksiyonlar. Hepsi ham (clean edilmiş) X alır, fiyat döndürür."""

import numpy as np
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.ml.config import CAT_COLS, NUM_COLS


def _with_log_target(pipeline: Pipeline) -> TransformedTargetRegressor:
    return TransformedTargetRegressor(regressor=pipeline, func=np.log1p, inverse_func=np.expm1)


def make_linear_model(alpha: float = 1.0) -> TransformedTargetRegressor:
    pre = ColumnTransformer(
        [
            ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUM_COLS),
            (
                "cat",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=20),
                ),
                CAT_COLS,
            ),
        ]
    )
    return _with_log_target(Pipeline([("pre", pre), ("reg", Ridge(alpha=alpha))]))
```

Notebook'ta:

```python
from src.ml.models import make_linear_model

linear = make_linear_model()
linear.fit(X_train, y_train)

print("eğitim   :", evaluate(linear, X_train, y_train))
print("doğrulama:", evaluate(linear, X_val, y_val))
```

**Kontrol et:**
- Doğrulama MAE'si baseline'dan belirgin şekilde küçük.
- Eğitim ve doğrulama sonuçları birbirine yakın (doğrusal modeller pek ezberlemez).
- Tek bir satırla dene: `linear.predict(X_val.head(3))` ve `y_val.head(3)` değerleri makul ölçüde yakın mı?

> **Kontrol noktası 3:** Baseline ve Ridge sonuçlarını getir. "Bu MAE iyi mi?" sorusunu birlikte cevaplayalım.

**Commit:** `feat(ml): ridge pipeline modeli`

---

## Adım 7: Ağaç tabanlı modeller (B8)

**Amaç:** Doğrusal olmayan ilişkileri yakalayan daha güçlü modelleri denemek ve karşılaştırmak.

**Kavram:** Doğrusal model "her yıl fiyat X kadar düşer" gibi düz kurallar öğrenir. Gerçekte ilişki kırıklıdır: lüks bir marka eski de olsa pahalıdır, ilk birkaç yılda değer kaybı daha hızlıdır. **Karar ağaçları** veriyi "yıl > 2015 mi? marka BMW mi?" gibi sorularla böler. Tek ağaç ezberlemeye çok yatkındır, o yüzden çok ağaç birleştirilir:

- **Random Forest:** Yüzlerce ağaç ayrı ayrı eğitilir ve ortalamaları alınır. Sağlam ve kolay ayarlanır.
- **Gradient Boosting (`HistGradientBoostingRegressor`):** Ağaçlar sırayla eğitilir; her yeni ağaç öncekilerin hatasını düzeltmeye çalışır. Tablo verisinde genelde en iyi sonucu verir ve büyük veride hızlıdır.

Ağaçlar ölçekleme istemez. Kategorileri one-hot yerine sıra numarasına (`OrdinalEncoder`) çevirmek yeterlidir ve çok daha hızlıdır.

**Yap:** `src/ml/models.py` dosyasına ekle. İlk üç import satırını dosyanın en üstündeki import'ların yanına taşı (`RANDOM_STATE`'i mevcut `src.ml.config` satırına ekle); fonksiyonlar dosyanın sonuna gelir.

```python
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder

from src.ml.config import RANDOM_STATE


def _tree_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("num", SimpleImputer(strategy="median"), NUM_COLS),
            (
                "cat",
                make_pipeline(
                    SimpleImputer(strategy="constant", fill_value="Bilinmiyor"),
                    OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                ),
                CAT_COLS,
            ),
        ]
    )


def make_tree_model(regressor) -> TransformedTargetRegressor:
    return _with_log_target(Pipeline([("pre", _tree_preprocessor()), ("reg", regressor)]))


def make_random_forest() -> TransformedTargetRegressor:
    return make_tree_model(
        RandomForestRegressor(
            n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_STATE
        )
    )


def make_hist_gb(**params) -> TransformedTargetRegressor:
    return make_tree_model(HistGradientBoostingRegressor(random_state=RANDOM_STATE, **params))
```

Notebook'ta karşılaştır:

```python
import time

from src.ml.models import make_hist_gb, make_linear_model, make_random_forest

candidates = {
    "baseline": DummyRegressor(strategy="median"),
    "ridge": make_linear_model(),
    "random_forest": make_random_forest(),
    "hist_gb": make_hist_gb(),
}

rows = []
for name, model in candidates.items():
    start = time.time()
    model.fit(X_train, y_train)
    train_m = evaluate(model, X_train, y_train)
    val_m = evaluate(model, X_val, y_val)
    rows.append(
        {"model": name, "train_mae": train_m["mae"], **val_m, "saniye": time.time() - start}
    )

pd.DataFrame(rows).sort_values("mae")
```

**Kontrol et:**
- Gerçek ilan verisinde ağaç modelleri genelde Ridge'i geçer, ama her zaman değil. Fiyat ile özellikler arasındaki ilişki düzgünse Ridge de kazanabilir. Hangisi kazanırsa Adım 8–9'da onunla devam et.
- **Aşırı öğrenme kontrolü:** `train_mae` değeri doğrulama `mae` değerinden çok çok küçükse (Random Forest'ta genelde öyledir) model biraz ezberliyor demektir. Önemli olan doğrulama skorudur, ama aradaki fark Adım 8'de neden ayar yaptığımızı gösterir.

> **Kontrol noktası 4:** Karşılaştırma tablosunu getir. Hangi modelle devam edeceğimize birlikte karar verelim.

**Commit:** `feat(ml): random forest ve gradient boosting modelleri`

---

## Adım 8: Çapraz doğrulama ve hiperparametre ayarı (B8)

**Amaç:** Seçtiğin modelin şans eseri iyi çıkmadığından emin olmak ve ayarlarını iyileştirmek.

**Kavram:**
- **Çapraz doğrulama:** Tek bir %20'lik bölme şanslı veya şanssız olabilir. Eğitim setini 5 parçaya böl; her seferinde 4'üyle eğit, 1'iyle ölç ve 5 sonucun ortalamasını al. Sonuç daha güvenilir olur.
- **Hiperparametre ayarı:** Öğrenme hızı, yaprak sayısı gibi ayarların farklı kombinasyonlarını dene, CV skoru en iyi olanı seç. `RandomizedSearchCV` tüm kombinasyonları değil, rastgele `n_iter` tanesini dener; bu da hızlıdır.
- Ayarı **yalnızca eğitim setinde** CV ile yap. Doğrulama seti son sınav olarak kalsın.

**Yap:** notebook'ta

```python
from sklearn.model_selection import KFold, RandomizedSearchCV, cross_val_score

cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

scores = cross_val_score(
    make_hist_gb(), X_train, y_train, cv=cv, scoring="neg_mean_absolute_error", n_jobs=-1
)
print(f"CV MAE: {-scores.mean():.0f} ± {scores.std():.0f}")
```

```python
# Parametre adları: TransformedTargetRegressor → "regressor" → Pipeline adımı "reg"
param_dist = {
    "regressor__reg__learning_rate": [0.03, 0.05, 0.1],
    "regressor__reg__max_leaf_nodes": [15, 31, 63],
    "regressor__reg__min_samples_leaf": [10, 20, 50],
    "regressor__reg__max_iter": [200, 400, 800],
}

search = RandomizedSearchCV(
    make_hist_gb(),
    param_dist,
    n_iter=20,
    cv=cv,
    scoring="neg_mean_absolute_error",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
search.fit(X_train, y_train)

print("En iyi CV MAE:", -search.best_score_)
print(search.best_params_)
print("Doğrulama:", evaluate(search.best_estimator_, X_val, y_val))
```

En iyi parametreleri `src/ml/models.py` dosyasına sabit olarak yaz. `make_final_model` hangi model kazandıysa onu döndürür (aşağıdaki örnekte gradient boosting):

```python
BEST_PARAMS = {  # Adım 8, RandomizedSearchCV sonucu (tarih: ____)
    "learning_rate": 0.05,
    "max_leaf_nodes": 31,
    "min_samples_leaf": 20,
    "max_iter": 400,
}


def make_final_model() -> TransformedTargetRegressor:
    return make_hist_gb(**BEST_PARAMS)
```

**Kontrol et:** Ayarlı modelin doğrulama MAE'si varsayılan ayarlardan daha iyi veya en azından aynı. Değilse varsayılanla devam etmek de geçerli bir karardır. Bunu `MODEL.md`'ye yaz.

**Commit:** `feat(ml): çapraz doğrulama ve hiperparametre araması` · `docs: MODEL.md deney sonuçları`

---

## Adım 9: Final model ve kayıt (B9)

**Amaç:** Tek komutla (`python -m src.ml.train`) modeli eğitip arayüzün kullanacağı dosyaları üretmek.

**Kavram:**
- Model seçilip ölçüldükten sonra **tüm etiketli veriyle** yeniden eğitilir. Daha çok veri daha iyi model demektir. Ölçümü bundan önce, doğrulama setinde yapmış oluyoruz.
- `joblib.dump` modeli (ön işleme dahil) tek dosyaya kaydeder. `model_meta.json` dosyasına sürüm, metrikler ve özellik listesi yazılır; arayüzün "Model hakkında" bölümü buradan okur.
- **Tahmin aralığı:** Doğrulama setinde, log ölçeğinde hataların %10 ve %90 yüzdeliklerini kaydediyoruz. Tahmin anında `fiyat × e^q` ile "olası aralık" verilir. Basit ama dürüst bir yöntemdir.

**Yap:** `src/ml/train.py` (`src.db.queries` fonksiyonları B5'te yazılır)

```python
"""Final modeli eğitir ve kaydeder. Çalıştırma: python -m src.ml.train"""

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.model_selection import train_test_split

from src.db import queries
from src.ml.config import FEATURES, RANDOM_STATE, TARGET
from src.ml.evaluate import evaluate
from src.ml.models import make_final_model

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "model.joblib"
META_PATH = MODEL_DIR / "model_meta.json"


def main() -> None:
    df = queries.load_cars()  # temizlenmiş ve filtrelenmiş veri (cars tablosu)
    X, y = df[FEATURES], df[TARGET]
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    # 1) Doğrulama setinde ölç
    model = make_final_model()
    model.fit(X_train, y_train)
    metrics = evaluate(model, X_val, y_val)

    # 2) Tahmin aralığı: log ölçeğinde hataların %10 ve %90 yüzdelikleri
    residuals = np.log1p(y_val) - np.log1p(model.predict(X_val))
    q_low, q_high = np.quantile(residuals, [0.10, 0.90])

    # 3) Final: tüm veriyle yeniden eğit ve kaydet
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
        **{k: float(v) for k, v in metrics.items()},
    }

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    META_PATH.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    queries.insert_model_run(meta, params=estimator.get_params())

    print(f"Model kaydedildi: {MODEL_PATH} (sürüm {meta['version']})")
    m = metrics
    print(f"Doğrulama: MAE={m['mae']:.0f}  RMSE={m['rmse']:.0f}  R²={m['r2']:.3f}")


if __name__ == "__main__":
    main()
```

**Kontrol et:**
```bash
python -m src.db.load_data
python -m src.ml.train
python -c "import joblib; m = joblib.load('models/model.joblib'); print(type(m))"
```
- `models/model.joblib` ve `models/model_meta.json` oluştu.
- `model_runs` tablosunda yeni bir satır var.
- Komutu iki kez çalıştırınca hata vermiyor.

> **Kontrol noktası 5:** `train` çıktısını ve `model_meta.json` içeriğini getir. Sonra `service.predict` fonksiyonunu birlikte bağlayalım (B10b).

**Commit:** `feat(ml): final eğitim betiği ve model kaydı`

---

## Adım 10: Modeli yorumla (B11)

**Amaç:** "Model neye bakıyor, nerede yanılıyor?" sorularını cevaplamak. Sunumda en çok sorulacak kısım budur.

**Kavram:**
- **Permutation importance:** Bir sütunun değerlerini rastgele karıştır, hatanın ne kadar arttığına bak. Çok artıyorsa model o sütuna çok güveniyordur.
- **Hata analizi:** Hataları gruplara (marka, fiyat aralığı) ayırıp modelin zayıf olduğu yerleri bul.

**Yap:** notebook'ta (Adım 8'deki en iyi modelle, doğrulama setinde)

```python
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance

model = search.best_estimator_  # veya make_final_model().fit(X_train, y_train)

result = permutation_importance(
    model, X_val, y_val, n_repeats=5, random_state=RANDOM_STATE,
    scoring="neg_mean_absolute_error", n_jobs=-1,
)
importance = pd.Series(result.importances_mean, index=X_val.columns).sort_values()
importance.plot.barh(title="Özellik önemi (MAE artışı)")
plt.savefig("docs/img/ozellik_onemi.png", dpi=150, bbox_inches="tight")
```

```python
errors = X_val.assign(gercek=y_val, tahmin=model.predict(X_val))
errors["mutlak_hata"] = (errors["gercek"] - errors["tahmin"]).abs()

# Hangi markalarda daha çok yanılıyoruz?
errors.groupby("brand")["mutlak_hata"].agg(["mean", "count"]).query("count >= 30").sort_values(
    "mean", ascending=False
).head(10)
```

```python
# Fiyat aralığına göre oransal hata
errors["fiyat_dilimi"] = pd.qcut(errors["gercek"], 5)
errors.assign(oransal=errors["mutlak_hata"] / errors["gercek"]).groupby(
    "fiyat_dilimi", observed=True
)["oransal"].median()
```

**Kontrol et:** `MODEL.md` §4–5'e grafik ve 3–4 maddelik yorum yazıldı.

**Commit:** `docs: özellik önemi ve hata analizi`

---

## Adım 11 (bonus): Kaggle gönderimi

**Amaç:** Yarışmaya bir tahmin dosyası göndermek ve skoru `MODEL.md`'ye yazmak.

**Yap:** `src/ml/predict_test.py`

```python
"""Kaggle test.csv için submission üretir. Çalıştırma: python -m src.ml.predict_test"""

import joblib
import pandas as pd

from src.ml.config import FEATURES
from src.ml.preprocess import clean

model = joblib.load("models/model.joblib")
test = clean(pd.read_csv("data/raw/test.csv"))  # DİKKAT: filter_train_rows YOK
sample = pd.read_csv("data/raw/sample_submission.csv")

submission = sample.copy()
submission[sample.columns[1]] = model.predict(test[FEATURES])  # sütun adları sample'a göre
submission.to_csv("data/submission.csv", index=False)
print(submission.head(), len(submission), "satır")
```

**Kontrol et:** Satır sayısı `sample_submission.csv` ile aynı. Kimlik (id) sütunu `test.csv`'deki sırayla eşleşiyor (gerekirse `sample.columns[0]` üzerinden birleştir).

---

## Sık karşılaşılan hatalar

| Belirti | Muhtemel neden | Çözüm |
|---|---|---|
| `KeyError: 'mileage'` | Sütun adı ham haliyle duruyor | `clean()` çağrıldı mı? `config.py`'deki adlar `DATA.md`'deki temiz adlarla aynı mı? |
| `could not convert string to float` | Metin sütunu `NUM_COLS` içinde ya da sayıya çevrilmemiş | Adım 2'de türü çevir veya sütunu `CAT_COLS`'a taşı |
| R² = 0,99, MAE çok küçük | **Veri sızıntısı:** ID veya fiyattan türetilmiş bir sütun özelliklerde | `FEATURES` listesini kontrol et |
| Tahminler negatif veya absürt | Log dönüşümü unutulmuş ya da kilometre gibi bir sütun yanlış ölçekte | `TransformedTargetRegressor` kullanılıyor mu? `describe()` ile kontrol et |
| `model.joblib` başka bilgisayarda yüklenmiyor | scikit-learn sürümleri farklı | `requirements.txt` sürümlerini sabitle |
| Eğitim çok uzun sürüyor | Veri büyük, Random Forest yavaş | Denemede `df.sample(...)`, `n_jobs=-1`, `n_iter` değerini küçült |
| Arayüzde model değişmiyor | Model ilk çağrıda önbelleğe alınıyor | Streamlit'i yeniden başlat |

## Kontrol noktaları özeti

| # | Ne zaman | Getireceğin | Birlikte yapacağımız |
|---|---|---|---|
| 1 | Adım 1 sonu | `shape`, `head`, `info`, eksik oranları, metin sütunu örnekleri | `DATA.md`, temizlik kararları, `CarInput` alanları |
| 2 | Adım 3 sonu | EDA grafikleri, korelasyon | EDA yorumları |
| 3 | Adım 6 sonu | Baseline ve Ridge metrikleri | Metrikleri yorumlama |
| 4 | Adım 7 sonu | Model karşılaştırma tablosu | Model seçimi |
| 5 | Adım 9 sonu | `train` çıktısı, `model_meta.json` | `service.predict` bağlantısı |
