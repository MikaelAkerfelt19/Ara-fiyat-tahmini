# Proje Planı: İkinci El Araç Fiyat Tahmini

> Python dersi dönem projesi · 2 kişi · Başlangıç: 9 Ekim 2026 · **Teslim: 9 Kasım 2026** (kesin tarihi buraya yazın)

## 1. Amaç

Kaggle "Used Car Price Prediction Challenge" verisini kullanarak bir aracın özelliklerinden ikinci el fiyatını tahmin eden bir model eğitmek, sonra bu modeli **tamamen Python ile yazılmış**, sade ve şık bir web arayüzüyle sunmak.

## 2. Kapsam

**Yapılacaklar**
- Verinin temizlenip SQLite veritabanına yüklenmesi
- En az üç modelin denenip karşılaştırılması, en iyisinin kaydedilmesi
- Tek sayfalık Streamlit arayüzü: tahmin formu, sonuç, son tahminler, model bilgisi
- Yapılan tahminlerin veritabanına kaydedilmesi
- README, deney günlüğü (`MODEL.md`) ve sunum

**Kapsam dışı**
- Kullanıcı girişi ve hesap sistemi
- Canlıya alma (vakit kalırsa bonus: Streamlit Community Cloud)
- Çoklu dil desteği

## 3. Mimari

```
data/raw/train.csv
        │
        ▼
src/db/load_data.py  ──►  data/cars.db (SQLite)
                              │      ▲
                              ▼      │ tahmin geçmişi, model kayıtları
                    src/ml/train.py  │
                              │      │
                              ▼      │
                 models/model.joblib │
                              │      │
                              ▼      │
                    src/core/service.py   ◄── tek ortak kapı
                              ▲
                              │ yalnızca service fonksiyonları
                              │
                    app.py (Streamlit arayüz)
```

**Temel kural:** Arayüz kodu veritabanına ya da model dosyasına doğrudan dokunmaz, yalnızca `service` fonksiyonlarını çağırır. Böylece iki kişi birbirini beklemeden paralel çalışır. Ayrıntılar [CONTRACT.md](CONTRACT.md) içinde.

## 4. Teknolojiler

| Katman | Seçim | Neden |
|---|---|---|
| Arayüz | Streamlit | HTML/CSS/JS yazmadan, tamamen Python ile sade bir web arayüzü kurulur |
| Veri işleme | pandas, numpy | Standart araçlar |
| Veritabanı | SQLite (Python'un `sqlite3` modülü) | Sunucu kurulumu yok, tek dosya, hoca tek komutla çalıştırır |
| Model | scikit-learn | `Pipeline` ile ön işleme modele gömülür; öğrenmesi en kolay kütüphane |
| Model kaydı | joblib | scikit-learn'ün önerdiği yöntem |
| Grafik (EDA) | matplotlib | Notebook'ta analiz için |
| Test, kalite | pytest, ruff, Streamlit `AppTest`, GitHub Actions | Her push ve PR'da otomatik kontrol; `main` her zaman çalışır kalır |
| Ortam | Python 3.12, venv | Kütüphanelerle en sorunsuz sürüm |

## 5. Klasör yapısı

```
car-price-prediction/
├── app.py                      # Streamlit giriş noktası (arayüz)
├── .streamlit/config.toml      # tema
├── src/
│   ├── __init__.py
│   ├── core/                   # SÖZLEŞME: iki tarafın buluştuğu yer
│   │   ├── __init__.py
│   │   ├── schemas.py          # CarInput, Prediction
│   │   ├── errors.py           # ModelNotReadyError
│   │   ├── api.py              # mock / gerçek servis seçici
│   │   ├── mock_service.py     # sahte servis (arayüz için)
│   │   └── service.py          # gerçek servis (backend)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── schema.py           # tablo oluşturma
│   │   ├── load_data.py        # CSV → temizle → DB
│   │   └── queries.py          # sorgu fonksiyonları
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── config.py           # sütun listeleri, sabitler
│   │   ├── preprocess.py       # clean(), filter_train_rows()
│   │   ├── models.py           # model kurucu fonksiyonlar
│   │   ├── evaluate.py         # metrikler
│   │   ├── train.py            # final eğitim + kayıt
│   │   └── predict_test.py     # (bonus) Kaggle submission
│   └── app/
│       ├── __init__.py
│       └── components.py       # arayüz yardımcıları (fiyat biçimi vb.)
├── notebooks/
│   ├── 01_tanima.ipynb
│   ├── 02_eda.ipynb
│   └── 03_modelleme.ipynb
├── tests/
├── docs/                       # bu planlama dosyaları
├── data/                       # .gitignore: raw/ ve cars.db
├── models/                     # .gitignore: model.joblib, model_meta.json
├── .github/                    # CI iş akışı ve PR şablonu
├── requirements.txt
├── pyproject.toml              # pytest ve ruff ayarları
├── README.md
├── CONTRIBUTING.md
├── AGENTS.md                   # kodlama ajanları için kurallar
└── .gitignore
```

## 6. Roller

| | Kaan Demir | `<arkadaş adı>` |
|---|---|---|
| Alan | Veri, veritabanı, model eğitimi, servis katmanı | Streamlit arayüzü |
| Görev listesi | [GOREVLER_BACKEND.md](GOREVLER_BACKEND.md) | [ARAYUZ_KONSEPT.md](ARAYUZ_KONSEPT.md) §9 |
| Rehber | [EGITIM_REHBERI.md](EGITIM_REHBERI.md) | [ARAYUZ_KONSEPT.md](ARAYUZ_KONSEPT.md) §8. Kod örnekli çözüm Kaan'da, bilerek repoda değil |
| Ek sorumluluk | Repo yönetimi, sözleşme ve mock'u ilk gün hazırlamak, arayüz PR'larını incelemek, haftalık eşleşmeyi yürütmek | Backend PR'larını okuyup soru sormak (öğrenmek için) |

**Ortak işler:** sözleşme değişiklikleri, entegrasyon, README, sunum.

## 7. Takvim

| Hafta | Tarih | Kaan (backend) | Arkadaş (arayüz) | Hafta sonu çıktısı |
|---|---|---|---|---|
| 0 | 9–11 Ekim | B0 repo kurulumu, B1 sözleşme ve mock | A0 ortam kurulumu | İkisi de repoyu klonlamış, mock çalışıyor |
| 1 | 12–18 Ekim | B2 veriyi tanıma, B3 temizlik, B4 EDA | A1 iskelet ve tema, A2 form, A3 bağımlı seçim | **M1** |
| 2 | 19–25 Ekim | B5 veritabanı, B6 baseline, B7 ilk model, B10a servis (seçenekler, geçmiş) | A4 doğrulama, A5 sonuç kartı, A6 geçmiş, A7 model bilgisi | Form seçenekleri gerçek DB'den geliyor |
| 3 | 26 Ekim–1 Kasım | B8 ağaç modelleri ve CV, B9 final model, B10b servis (tahmin) | A8 önbellek, A9 gerçek servise geçiş | **M2** |
| 4 | 2–8 Kasım | B11 testler, yorumlama, Kaggle submission | A10 testler, ekran görüntüleri, README | **M3** (6 Kasım), 7–8 Kasım tampon |

29 Ekim resmi tatil olduğu için 3. hafta bir gün kısa.

## 8. Kilometre taşları

**M1: Uçtan uca iskelet (18 Ekim)**
- [ ] `USE_MOCK=1 streamlit run app.py` ile form doldurulup sahte bir tahmin görülebiliyor
- [ ] Kod `main` dalında, iki kişide de çalışıyor
- [ ] `DATA.md` veri sözlüğü dolu, temizlik kararları yazılmış

**M2: Gerçek model (1 Kasım)**
- [ ] `python -m src.db.load_data` → `python -m src.ml.train` → `streamlit run app.py` sırasıyla çalışınca gerçek tahmin geliyor
- [ ] Seçilen model, doğrulama setinde baseline'ı açık farkla geçiyor (`MODEL.md`'de sayılarla)
- [ ] Tahminler `predictions` tablosuna kaydediliyor ve arayüzde görünüyor

**M3: Teslim (6 Kasım)**
- [ ] `pytest` ve `ruff check .` temiz
- [ ] README'de kurulum, çalıştırma ve ekran görüntüsü var
- [ ] `MODEL.md` tamamlanmış: deneyler, seçilen model, özellik önemleri
- [ ] `v1.0` etiketi atılmış, final model GitHub Releases'e eklenmiş
- [ ] Sunum hazır

## 9. Haftalık rutin

| Ne zaman | Ne | Süre |
|---|---|---|
| Pazartesi | Haftanın issue'larını seç, panoda "Yapılıyor"a çek | 15 dk |
| Hafta içi | Küçük commit'ler. PR'lar 24 saat içinde incelenir | |
| Perşembe | **Entegrasyon günü:** açık PR'lar birleştirilir, `main` iki kişide de çalıştırılır | 30 dk |
| Pazar | Demo ve bu planın güncellenmesi. Kaan arayüz tarafındaki takılmaları burada çözer | 30 dk |

## 10. Riskler

| Risk | Etki | Önlem |
|---|---|---|
| Veri kirli (sayılar metin halinde, eksik değerler) | Temizlik uzar | Rehber Adım 2. Kararlar `DATA.md`'ye yazılır |
| Kaan'ın ilk model eğitimi deneyimi | Hafta 2–3 kayabilir | Adım adım rehber, kontrol noktaları, erken baseline |
| Entegrasyon sona kalır | Son hafta panik | İlk gün sözleşme ve mock, her perşembe birleştirme |
| Kategori sayısı çok (yüzlerce model adı) | Model ağırlaşır veya bozulur | Seyrek kategorileri gruplamak (`min_frequency`) |
| Eğitimde ve tahminde farklı ön işleme | Arayüzde saçma tahminler | Ön işleme `Pipeline` içinde, temizlik tek fonksiyonda |
| Model dosyası büyük | Repo şişer | `.gitignore` + GitHub Releases |
| scikit-learn sürümü iki bilgisayarda farklı | Model yüklenmez | `requirements.txt` sürümleri sabitlenir (B0) |

## 11. Belgeler

- [CONTRACT.md](CONTRACT.md): servis sözleşmesi
- [GOREVLER_BACKEND.md](GOREVLER_BACKEND.md): Kaan'ın görevleri
- [EGITIM_REHBERI.md](EGITIM_REHBERI.md): model eğitimi rehberi
- [ARAYUZ_KONSEPT.md](ARAYUZ_KONSEPT.md): arayüz konsepti ve görevleri
- [CODEX_GOREV.md](CODEX_GOREV.md): Codex Görevi #1, proje temelleri
- [DATA.md](DATA.md): veri sözlüğü
- [MODEL.md](MODEL.md): deney günlüğü
- [../CONTRIBUTING.md](../CONTRIBUTING.md): git kuralları
- [../AGENTS.md](../AGENTS.md): kodlama ajanları için kurallar
