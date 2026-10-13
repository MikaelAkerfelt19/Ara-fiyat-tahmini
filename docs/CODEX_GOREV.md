# Codex Görevi #1: Projenin Temellerini At

> Hazırlayan: Kaan (Claude ile planlandı) · Tarih: 13 Ekim 2026 · Kapsam: `GOREVLER_BACKEND.md` B0'ın kod kısmı ve B1
> Ajanın bu belgeden önce `AGENTS.md` dosyasını okumuş olması gerekir.

Belgenin bölümleri:
- **§0** Kaan'ın Codex'i nasıl çalıştıracağı
- **§1–2** Projenin geçmişi ve alınan kararlar (bağlam)
- **§3** Codex'in yapacağı iş
- **§4** Codex'e yapıştırılacak komut
- **§5** Sonraki adımlar

---

## 0. Kullanım (Kaan için)

1. GitHub'da boş bir repo aç: `car-price-prediction`. README eklemeden oluştur.
2. Repoyu klonla. Bu paketin içeriğini repo köküne kopyala (`AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `.gitignore`, `requirements.txt`, `pyproject.toml`, `docs/`).
3. Bu belgeleri ilk commit olarak doğrudan `main` dalına gönder. Repo boş olduğu için bu bir kerelik bir istisna:
   ```bash
   git add .
   git commit -m "docs: proje planı, sözleşme ve ajan kuralları"
   git push -u origin main
   ```
4. Repoda Codex'i aç ve **§4'teki komutu** yapıştır.
5. Codex `feature/core-iskelet` dalında çalışıp commit'leri atacak. Sonunda bir rapor verecek.
6. Raporu ve değişiklikleri incele. Kabul komutlarını (§3.5) kendin de çalıştır. Sonra dalı push et ve PR aç. PR'ı arkadaşın incelesin; bu onun için de iyi bir başlangıç olur. Sonra birleştir.
7. §5'teki GitHub ayarlarına geç.

---

## 1. Bağlam: proje ve bu noktaya nasıl gelindi

### 1.1 İstek

- Kaggle **Used Car Price Prediction Challenge** verisiyle ikinci el araç fiyatı tahmin edilecek. (https://www.kaggle.com/competitions/used-car-price-prediction-challenge)
- Proje bir **Python dersi ödevi.** Arayüz dahil **her şey Python** ile yazılacak. Bu kesin bir şart.
- Arayüz **minimalist**: sade ve şık olmalı.
- **İki kişi** çalışıyor: Kaan veritabanı ve model eğitimini (backend) yapıyor, arkadaşı arayüzü (frontend).
- Ortak bir **GitHub reposu** var. Her geliştirme commit'lenecek, hoca commit geçmişine bakabilir.
- Planlama markdown dosyalarıyla yapılıyor.
- Teslim tarihi: **9 Kasım 2026** (istekten bir ay sonra).
- Hoca **web arayüzünü kabul ediyor.** Veritabanı türü fark etmiyor.
- Kaan **daha önce hiç model eğitmedi.** Eğitimi adım adım öğrenerek yapacak.

### 1.2 Veri seti hakkında bilinenler

- Kaggle'ın yarışma sayfası giriş yapmadan ayrıntıları göstermiyor. Bilinenler: bu bir **regresyon** görevi, veri **internetteki ilan sitelerinden toplanmış gerçek ilanlar.**
- **Sütun adları, değerlendirme metriği ve para birimi henüz bilinmiyor.** Kaan veriyi indirip inceleyince (`EGITIM_REHBERI.md` Adım 1, Kontrol noktası 1) `docs/DATA.md` dolacak. `CarInput` alanları da o zaman kesinleşecek.
- Veriyi indirmek için Kaggle'da yarışmaya katılıp kuralları kabul etmek gerekiyor. Yarışma verisi genelde yeniden paylaşılamadığı için **veri repoya konmuyor**; herkes kendi bilgisayarına `data/raw/` altına indiriyor.

### 1.3 Kararlar

| Konu | Karar | Neden |
|---|---|---|
| Arayüz | **Streamlit** | Tamamen Python. HTML/CSS/JS yazmadan sade bir web sayfası kurulur |
| Veritabanı | **SQLite** (`sqlite3`) | Sunucu kurulumu yok, tek dosya, hoca tek komutla çalıştırır |
| Model | **scikit-learn** `Pipeline` | Ön işleme modele gömülür; arayüzden gelen ham satır doğrudan modele verilir |
| Model sırası | Medyan baseline → Ridge → Random Forest → HistGradientBoosting → çapraz doğrulama ve ayar | Basitten karmaşığa, her adım ölçülerek ilerlenir |
| Hedef | `log(1 + fiyat)` (`TransformedTargetRegressor`) | Fiyat çarpık; model oransal hatayı küçültür |
| Ana metrik | **MAE** (ek olarak RMSE, R²) | En kolay yorumlanan metrik: "ortalama X para birimi yanılıyoruz" |
| Tahmin aralığı | Doğrulama setindeki log hatalarının %10 ve %90 yüzdelikleri | Basit ve dürüst bir "olası aralık" |
| Model kaydı | `models/model.joblib` ve `models/model_meta.json` | Repoya girmez; final model GitHub Releases'e eklenir |
| İki kişinin buluşma noktası | **Servis sözleşmesi** ve **sahte servis** (`USE_MOCK=1`) | Arayüz, model hazır olmadan geliştirilebilir; iki kişi birbirini beklemez |
| Ortam | Python 3.12, venv, sabitlenmiş `requirements.txt` | scikit-learn sürümü iki bilgisayarda farklı olursa model dosyası yüklenmez |
| Kalite | pytest, ruff, Streamlit `AppTest`, GitHub Actions | `main` her zaman çalışır kalsın |
| Git | `main` korumalı, dallar ve PR, birbirinin PR'ını inceleme, merge commit | Düzenli ve iki kişinin de göründüğü bir commit geçmişi |

### 1.4 Mimari

```
data/raw/train.csv ─► src/db/load_data.py ─► data/cars.db (SQLite)
                                                   │
                                          src/ml/train.py ─► models/model.joblib
                                                   │
                         src/core/service.py  ◄────┘   (gerçek servis, Kaan)
                         src/core/mock_service.py      (sahte servis, şimdilik)
                                   ▲
                                   │  from src.core.api import service
                                   │
                                app.py  (Streamlit, arkadaş)
```

`src/core/api.py`, `USE_MOCK` ortam değişkenine bakarak sahte veya gerçek servisi verir. Arayüz hangisinin geldiğini bilmez.

### 1.5 İş bölümü ve öğrenme ilkesi

- **Kaan (backend):** Görevleri `docs/GOREVLER_BACKEND.md` (B0–B11) içinde. Model eğitimini `docs/EGITIM_REHBERI.md` ile adım adım öğrenecek. Rehberde 5 kontrol noktası var; her birinde çıktılar Claude ile birlikte yorumlanacak. **Bu yüzden model kodunu ajan yazmayacak.**
- **Arkadaş (frontend):** Kod örneği içermeyen bir konsept belgesi aldı: `docs/ARAYUZ_KONSEPT.md`. Bu belge ekranı, davranış kurallarını, tasarım ilkelerini ve görevleri (A0–A10) kabul ölçütleriyle anlatıyor. Kodu kendisi yazacak. **Bu yüzden arayüzü ajan yazmayacak.**
- Arayüz görevlerinin kod örnekli bir çözümü Kaan'da duruyor, ama bilerek repoya konmadı.

### 1.6 Takvim

| Hafta | Tarih | Kilometre taşı |
|---|---|---|
| 0 | 9–11 Ekim | Plan ve belgeler (tamam) |
| 1 | 12–18 Ekim | **M1:** Sahte servisle çalışan form. Veri sözlüğü dolu |
| 2 | 19–25 Ekim | Veritabanı, baseline ve ilk model. Arayüz bölümleri |
| 3 | 26 Ekim – 1 Kasım | **M2:** Gerçek modelle çalışan uygulama |
| 4 | 2–8 Kasım | **M3 (6 Kasım):** Testler, yorumlama, README, sunum. `v1.0` etiketi |

### 1.7 Şimdiye kadar yapılan doğrulama

- Belgelerdeki bütün kod (veri yükleme, temizlik, EDA, model karşılaştırması, çapraz doğrulama, final eğitim, Kaggle gönderimi, gerçek servis, arayüzün dolu hali ve testleri) **sahte bir veri setiyle uçtan uca hatasız çalıştırıldı.**
- Bu belgedeki §3 görevi de önceden aynı şekilde denendi. Sonuç: 17 test geçti, `ruff check` ve `ruff format --check` temiz, `streamlit run app.py` sayfayı açıyor. Denerken çıkan tuzaklar §3.3'te.

### 1.8 Açık konular (bu görevde çözülmeyecek)

- Veri setinin sütun adları, `CarInput` alanları, para birimi ve yarışma metriği (Kontrol noktası 1'de belli olacak)
- Arkadaşın adı ve GitHub kullanıcı adı (`README.md` içinde `<arkadaş adı>`, `<kullanici>` yer tutucuları)

---

## 2. Repoda şu an ne var?

| Dosya | İçerik |
|---|---|
| `AGENTS.md` | Ajan kuralları |
| `README.md` | Kurulum, veriyi indirme, çalıştırma, belge listesi |
| `CONTRIBUTING.md` | Dal, commit ve PR kuralları |
| `.gitignore` | `data/`, `*.db`, `models/*` (`.gitkeep` hariç), `kaggle.json`, `.venv/` vb. |
| `requirements.txt` | Bağımlılıklar (henüz **sabitlenmemiş**) |
| `pyproject.toml` | pytest (`pythonpath = ["."]`) ve ruff ayarları (`*.md` ve `notebooks` hariç) |
| `docs/PLAN.md` | Genel plan, mimari, klasör yapısı, takvim, riskler |
| `docs/CONTRACT.md` | Servis sözleşmesi: veri sınıfları, hatalar, fonksiyonlar, `api.py`, sahte servis, tablo şemaları |
| `docs/GOREVLER_BACKEND.md` | Kaan'ın görevleri (B0–B11), veritabanı ve gerçek servis tasarımı |
| `docs/EGITIM_REHBERI.md` | Model eğitimi rehberi (Adım 0–11) |
| `docs/ARAYUZ_KONSEPT.md` | Arayüz konsepti ve görevleri (A0–A10) |
| `docs/DATA.md`, `docs/MODEL.md` | Veri sözlüğü ve deney günlüğü şablonları |
| `docs/CODEX_GOREV.md` | Bu belge |

Henüz **hiç Python kodu yok.**

---

## 3. Görev: temeller

### 3.1 Yapılacaklar

**1. Klasör iskeleti** (`docs/PLAN.md` §5)
- Boş `__init__.py` dosyaları: `src/`, `src/core/`, `src/db/`, `src/ml/`, `src/app/`
- `.gitkeep` dosyaları: `models/`, `notebooks/`, `docs/img/`
- `data/` klasörü oluşturulmaz, çünkü `.gitignore` kapsamında.

**2. Sözleşme kodu**: `docs/CONTRACT.md` içindeki kod **birebir** kullanılır.
- `src/core/schemas.py` ← §1
- `src/core/errors.py` ← §2
- `src/core/api.py` ← §4
- `src/core/mock_service.py` ← §5

`CarInput` içindeki `# TODO(Hafta 1)` yorumu korunur. Yer tutucu alanlar değiştirilmez.

**3. Gerçek servis taslağı**: `src/core/service.py`
- Sahte servisle **aynı 7 fonksiyon ve aynı imzalar**: `get_options`, `get_models_for_brand`, `get_ranges`, `predict`, `save_prediction`, `get_history`, `get_model_info`.
- Her fonksiyonun gövdesi, Türkçe ve yol gösterici bir mesajla `NotImplementedError` fırlatır. Örnek: `"Henüz yazılmadı (GOREVLER_BACKEND.md, B10). Şimdilik USE_MOCK=1 kullanın."`
- Yalnızca `src.core.schemas` içe aktarılır. `src.db` veya `src.ml` içe aktarılmaz, çünkü henüz yoklar.
- Modül docstring'i dosyanın taslak olduğunu ve B10'da yazılacağını belirtir.

**4. Boş uygulama sayfası**: `app.py`
- Bir modül docstring'i, `import streamlit as st` ve tek satır: `st.title("İkinci El Araç Fiyat Tahmini")`.
- **Başka hiçbir şey yazılmaz.** Sayfa ayarları, tema, form vb. arkadaşın görevleridir (A1–A10). `.streamlit/` klasörü de oluşturulmaz.

**5. Testler**
- `tests/conftest.py`: `os.environ["USE_MOCK"] = "1"` ayarlar. Docstring'i "Testler her zaman sahte servisle çalışır." olur.
- `tests/test_contract.py`: sözleşme uyum testleri. Şunları denetler:
  - 7 fonksiyonun her biri için `inspect.signature(mock_service.f) == inspect.signature(service.f)` (parametreli test)
  - `get_options()`: `"brand"` anahtarı var, `"model"` anahtarı yok, her liste alfabetik sıralı ve tekrarsız
  - `get_models_for_brand("Yok") == []`
  - `get_ranges()`: her aralıkta `alt < üst`
  - `predict()`: dönen değer bir `Prediction` ve `low <= price <= high`
  - Negatif kilometrede `ValueError`
  - `save_prediction` ile iki kayıt eklenince `get_history(2)` en yeniyi üstte döndürüyor; satırlarda `created_at` ve `price` var
  - `get_model_info()` anahtarları tam olarak şunlar: `model_name`, `version`, `trained_at`, `mae`, `rmse`, `r2`, `n_train`
  - `src.core.api`: `USE_MOCK=1` iken `service is mock_service`, `USE_MOCK=0` iken `service is src.core.service` (parametreli test, §3.3 madde 2'ye dikkat)
- `tests/test_smoke.py`: uygulama sahte servisle hatasız açılıyor (`AppTest`, `assert not at.exception`). §3.3 madde 3'e dikkat.
- `tests/test_app.py` ve `tests/test_components.py` **oluşturulmaz**, bunlar arkadaşın dosyaları.

**6. CI**: `.github/workflows/ci.yml` (önceden denendi, aynen kullanılabilir)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      USE_MOCK: "1"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: ruff format --check .
      - run: pytest
```

**7. PR şablonu**: `.github/pull_request_template.md` (`CONTRIBUTING.md` §5'e göre)

```markdown
## Ne değişti?
-

## Nasıl test ettim?
- [ ] `ruff check .` ve `ruff format --check .`
- [ ] `pytest`
- [ ] Arayüz değişikliğiyse: `USE_MOCK=1 streamlit run app.py` ile elle denendi

## Ekran görüntüsü
(Arayüz değişikliği varsa)

Closes #
```

**8. Sürümleri sabitle**: `requirements.txt`
- Python 3.12 ortamında `pip install -r requirements.txt` çalıştır.
- Dosyadaki **9 doğrudan bağımlılığı** kurulan sürümle `paket==sürüm` biçiminde sabitle: `streamlit`, `pandas`, `numpy`, `scikit-learn`, `joblib`, `matplotlib`, `jupyter`, `pytest`, `ruff`.
- `pip freeze` çıktısının tamamını **yapıştırma.** Dosyanın başındaki açıklama yorumunu "sürümler sabitlendi, scikit-learn sürümü iki bilgisayarda aynı olmalı" anlamında güncelle.
- Ortamında Python 3.12 yoksa ya da ağ erişimi yoksa sürümleri **uydurma.** Dosyayı olduğu gibi bırak ve raporda belirt.

### 3.2 Kapsam dışı (yapma)

- `src/db/` ve `src/ml/` altına `__init__.py` dışında dosya ekleme (`config.py`, `preprocess.py`, `schema.py` vb. Kaan'ın öğrenme görevleri).
- `app.py`'ye başlık dışında bir şey ekleme. `.streamlit/config.toml` ve `src/app/components.py` oluşturma.
- `docs/` altındaki belgeleri değiştirme. Bir çelişki görürsen raporda yaz.
- Veri indirme, notebook oluşturma, model eğitme.
- README'deki `<kullanici>` ve `<arkadaş adı>` yer tutucularını doldurma.

### 3.3 Tuzaklar (önceki denemede yaşandı)

1. **ruff Markdown dosyalarını da biçimlendirmeye çalışıyor.** Yeni ruff sürümleri `.md` dosyalarındaki kod bloklarını da kontrol ediyor ve belgeler yüzünden `ruff format --check` başarısız oluyor. `pyproject.toml`'daki `extend-exclude = ["*.md", "notebooks"]` satırı bunu çözüyor; **bu satırı kaldırma.**
2. **`api` testi modülü değiştirilmiş halde bırakmamalı.** `USE_MOCK=0` ile `importlib.reload(src.core.api)` yapan test, işi bitince ortamı geri alıp (`monkeypatch.undo()`) modülü yeniden yüklemeli (`try/finally`). Yoksa ileride `app.py` servisi içe aktardığında duman testi gerçek (henüz yazılmamış) servisi alıp çöker.
3. **`AppTest` süresi.** Varsayılan 3 saniye, soğuk başlangıçta yetmiyor; ilk denemede bir kez zaman aşımı yaşandı. `AppTest.from_file(<mutlak yol>, default_timeout=30)` kullan. Mutlak yolu `Path(__file__).resolve().parents[1] / "app.py"` ile kur.

### 3.4 Commit planı

Dal: `feature/core-iskelet` (güncel `main`'den açılır). Her commit'ten sonra ruff ve pytest temiz kalmalı.

| # | Commit mesajı | İçerik |
|---|---|---|
| 1 | `chore: klasör iskeletini oluştur` | `__init__.py` ve `.gitkeep` dosyaları |
| 2 | `chore: bağımlılık sürümlerini sabitle` | `requirements.txt` |
| 3 | `feat(core): servis sözleşmesi ve sahte servis` | `schemas.py`, `errors.py`, `api.py`, `mock_service.py` |
| 4 | `feat(core): gerçek servis taslağı` | `service.py` |
| 5 | `feat(ui): başlıklı boş sayfa` | `app.py` |
| 6 | `test(core): sözleşme uyum ve duman testleri` | `conftest.py`, `test_contract.py`, `test_smoke.py` |
| 7 | `chore: CI iş akışı ve PR şablonu` | `.github/` |

2. adım yapılamazsa atlanır ve raporda belirtilir.

### 3.5 Kabul ölçütleri

```bash
ruff check .                     # All checks passed!
ruff format --check .            # ... files already formatted
pytest                           # hepsi geçer (beklenen: 17 civarı test)
USE_MOCK=1 python -c "from src.core.api import service; print(service.get_options())"
                                 # sahte seçenekleri yazdırır
USE_MOCK=1 streamlit run app.py  # başlığı olan boş bir sayfa açar
git log --oneline main..HEAD     # §3.4'teki commit'ler
git status                       # temiz; data/, models/*.joblib, .venv/ izlenmiyor
```

Ayrıca:
- `src/core/` altındaki dört dosya `docs/CONTRACT.md` ile birebir aynı.
- `src/db/` ve `src/ml/` altında yalnızca `__init__.py` var.

### 3.6 Rapor biçimi

1. Yapılanların özeti (3–5 madde)
2. Oluşturulan ve değişen dosyalar
3. Commit listesi (`git log --oneline main..HEAD`)
4. §3.5 komutlarının çıktısı
5. Sabitlenen sürümler (veya neden sabitlenemedikleri)
6. Belgelerde gördüğün çelişkiler ve açık sorular

---

## 4. Codex'e yapıştırılacak komut

```text
Bu repoda önce AGENTS.md'yi, sonra docs/CODEX_GOREV.md'yi baştan sona oku.
docs/CODEX_GOREV.md §3'teki görevi uygula:
- Güncel main'den feature/core-iskelet dalını aç ve §3.4'teki commit planına uy.
- §3.2'deki kapsam dışı işlerin hiçbirini yapma; §3.3'teki tuzaklara dikkat et.
- src/core altındaki dört dosyada docs/CONTRACT.md'deki kodu birebir kullan.
- Bitirince §3.5'teki kabul komutlarını çalıştır ve §3.6'daki biçimde rapor ver.
- Push etme, PR açma.
Belirsiz bir şey olursa tahmin yürütme; dur ve sor.
```

---

## 5. Sonra ne olacak?

**Kaan, GitHub'da elle yapılacaklar** (`GOREVLER_BACKEND.md` B0):
- [ ] Arkadaşı **Settings → Collaborators** ile ekle.
- [ ] Codex'in PR'ı birleştikten sonra `main` için "Require a pull request before merging" ve "Require status checks to pass" (CI) kurallarını aç. Özel repolarda GitHub Pro gerekebilir; GitHub Student Developer Pack ile ücretsiz.
- [ ] **Projects** panosu (Yapılacak → Yapılıyor → İncelemede → Bitti), etiketler (`ui`, `db`, `ml`, `core`, `docs`, `bug`) ve milestone'lar (M1 18 Ekim, M2 1 Kasım, M3 6 Kasım).
- [ ] `GOREVLER_BACKEND.md` (B2–B11) ve `ARAYUZ_KONSEPT.md` §9 (A0–A10) içindeki her görev için bir issue.

**Arkadaş:** Repoyu klonlar, A0'ı yapar (`USE_MOCK=1 streamlit run app.py` başlıklı boş sayfayı açmalı) ve A1'den devam eder.

**Kaan:** `EGITIM_REHBERI.md` Adım 0–1. Veriyi indirir, `01_tanima.ipynb` çıktılarını Claude'a getirir (**Kontrol noktası 1**). Sütunlar kesinleşince yapılacak iş Codex'e verilebilecek kadar mekanik olur: **Codex Görevi #2**: `CONTRACT.md`, `schemas.py`, `mock_service.py` ve sözleşme testlerini kesinleşen alanlara göre güncellemek.

**Codex'i sonraki görevlerde kullanırken:**
- Her seferinde tek bir issue ver. Kapsamı ve kabul ölçütünü yaz, "push etme" de.
- `src/ml/` ve `notebooks/` için kod yazdırma; takıldığın yerde açıklama iste (`AGENTS.md` bunu zaten söylüyor).
- Codex'in ürettiği her değişikliği PR olarak arkadaşınla incele. Sunumda her satırı açıklayabilmen gerekiyor.
