# İkinci El Araç Fiyat Tahmini

Kaggle **Used Car Price Prediction Challenge** verisiyle bir aracın özelliklerinden ikinci el fiyatını tahmin eden, baştan sona Python ile yazılmış bir web uygulaması. Python dersi dönem projesidir.

## Ekip

| Kişi | Sorumluluk |
|---|---|
| Kaan Demir | Veri, veritabanı, model eğitimi, servis katmanı (backend) |
| `<arkadaş adı>` | Streamlit arayüzü (frontend) |

## Teknolojiler

Python 3.12 · Streamlit · pandas · scikit-learn · SQLite · joblib · pytest · ruff

## Kurulum

```bash
git clone https://github.com/<kullanici>/car-price-prediction.git
cd car-price-prediction
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## Veriyi indirme

Veri setini repoya koymuyoruz. Herkes kendi bilgisayarına indirir.

1. Kaggle'da yarışma sayfasına gir, **Join Competition** ile katıl ve kuralları kabul et.
2. **Data** sekmesinden **Download All** ile zip'i indir.
3. Zip'in içindekileri `data/raw/` klasörüne çıkar (`data/raw/train.csv` vb.).

Kaggle CLI kullanmak istersen: `kaggle competitions download -c used-car-price-prediction-challenge -p data/raw`. Bunun için Kaggle API anahtarın gerekir. **Anahtar dosyasını (`kaggle.json`) asla repoya ekleme.**

## Çalıştırma

```bash
python -m src.db.load_data      # data/cars.db dosyasını oluşturur
python -m src.ml.train          # models/model.joblib dosyasını üretir
streamlit run app.py            # arayüzü açar
```

Model henüz hazır değilken arayüz sahte (mock) servisle çalışır:

```bash
# macOS/Linux
USE_MOCK=1 streamlit run app.py
# Windows PowerShell
$env:USE_MOCK="1"; streamlit run app.py
```

## Testler

```bash
pytest
ruff check . && ruff format --check .
```

## Proje belgeleri

| Belge | İçerik |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | Genel plan, mimari, takvim, kilometre taşları |
| [docs/CONTRACT.md](docs/CONTRACT.md) | Arayüz ile backend'in buluştuğu servis sözleşmesi |
| [docs/GOREVLER_BACKEND.md](docs/GOREVLER_BACKEND.md) | Veri, DB ve model görevleri |
| [docs/EGITIM_REHBERI.md](docs/EGITIM_REHBERI.md) | Sıfırdan model eğitimi, adım adım |
| [docs/ARAYUZ_KONSEPT.md](docs/ARAYUZ_KONSEPT.md) | Arayüz konsepti: ekran, davranışlar, görevler, kabul ölçütleri |
| [docs/DATA.md](docs/DATA.md) | Veri sözlüğü ve temizlik kararları |
| [docs/MODEL.md](docs/MODEL.md) | Model deney günlüğü ve sonuçlar |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Git akışı, commit ve PR kuralları |
| [AGENTS.md](AGENTS.md) | Kodlama ajanları (Codex vb.) için proje kuralları |
| [docs/CODEX_GOREV.md](docs/CODEX_GOREV.md) | Codex Görevi #1: proje temelleri ve bu noktaya kadar alınan kararlar |

## Ekran görüntüsü

_(4. haftada eklenecek: `docs/img/arayuz.png`)_
