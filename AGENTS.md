# AGENTS.md

Bu dosya, bu repoda çalışan kodlama ajanları (Codex vb.) için kalıcı kurallardır. Her oturumun başında okunur.

## Proje

İkinci el araç fiyat tahmini. Kaggle *Used Car Price Prediction Challenge* verisiyle eğitilen bir regresyon modeli ve bu modeli sunan tek sayfalık bir web arayüzü. Python dersi dönem projesi. İki kişilik ekip, teslim tarihi 9 Kasım 2026.

**Kesin şart:** Her şey Python ile yazılır. Arayüz Streamlit, veritabanı SQLite, model scikit-learn.

## Ekip ve Codex kapsamı

- Backend sorumlusu: Kaan (`MikaelAkerfelt19`).
- Frontend sorumlusu: `meng-IO`.
- Codex'in uygulama geliştirme görevleri backend kapsamındadır. Frontend kodu ve
  frontend özellikleri `meng-IO` tarafından geliştirilir; bu oturumlarda frontend
  uygulaması yapılmaz. Ortak servis sözleşmesi ve repo kurulumu backend görevlerine dahildir.

Çalışmaya başlamadan önce şunları oku:
1. `docs/PLAN.md`: mimari, klasör yapısı, takvim
2. `docs/CONTRACT.md`: arayüz ile backend arasındaki servis sözleşmesi
3. `CONTRIBUTING.md`: git kuralları

## Sahiplik ve sınırlar

Bu repoda iki insan geliştirici var. İkisi de projeyi **öğrenerek** yapıyor. Ajan yalnızca kendisine **açıkça verilen görevi** yapar ve kapsamı kendiliğinden genişletmez.

| Alan | Sahibi | Ajan için kural |
|---|---|---|
| `src/core/` | Ortak (sözleşme) | Yalnızca görev açıkça istiyorsa değiştir. Önce `docs/CONTRACT.md` güncellenir, kod aynı commit'te onu izler |
| `src/db/` | Kaan | Yalnızca Kaan'ın açıkça verdiği görevi yap. Tasarım `docs/GOREVLER_BACKEND.md` B5'te |
| `src/ml/`, `notebooks/` | Kaan | Kaan model eğitimini ilk kez öğreniyor. Bu alanlarda **kodu toptan yazma.** Yardım istenirse `docs/EGITIM_REHBERI.md`'deki adımı açıkla, yalnızca istenen parçayı yaz, her satırın ne yaptığını anlat |
| `app.py`, `.streamlit/`, `src/app/`, `tests/test_app.py`, `tests/test_components.py` | Arayüz geliştiricisi | Arayüz özelliklerini, o kişi açıkça istemedikçe yazma. Hedefler `docs/ARAYUZ_KONSEPT.md` içinde |
| `docs/` | Ortak | Kodla çelişen bir belge görürsen düzeltme, raporunda belirt |

**Hiçbir zaman:**
- Kaggle verisini indirmeye çalışma ve `data/`, `models/`, `*.db`, `kaggle.json` dosyalarını commit'leme.
- Veri setinin sütun adlarını tahmin edip uydurma. Kesin adlar `docs/DATA.md` dolunca belli olacak. O zamana kadar `docs/CONTRACT.md`'deki yer tutucu alanlar kullanılır.
- Sayfaya HTML, CSS veya JavaScript gömme (`unsafe_allow_html`, `components.html` vb. kullanma). Görünüm yalnızca Streamlit bileşenleri ve `.streamlit/config.toml` ile ayarlanır.

## Teknik kurallar

- Python 3.12. Bağımlılıklar `requirements.txt` içinde, sürümleri sabitlenmiş.
- Arayüz servise yalnızca şu yoldan ulaşır: `from src.core.api import service`. Veritabanına veya model dosyasına doğrudan erişmez.
- `src/core/mock_service.py` ve `src/core/service.py` **birebir aynı fonksiyon imzalarına** sahiptir. `tests/test_contract.py` bunu denetler.
- İsimler (değişken, fonksiyon, dosya) İngilizce olur. Yorumlar, docstring'ler, arayüz metinleri ve commit mesajları Türkçe olur.
- `src/core/` altında tip ipuçları zorunludur.
- SQLite: Her fonksiyon kendi bağlantısını açıp kapatır. Kullanıcıdan gelen değerler her zaman `?` parametresiyle verilir.
- Model: Ön işleme scikit-learn `Pipeline` içinde tutulur. `clean()` hiçbir zaman satır silmez; `filter_train_rows()` yalnızca eğitim verisine uygulanır.
- Satır uzunluğu en fazla 100 karakter. ruff ayarları `pyproject.toml`'da; `*.md` dosyaları ve `notebooks/` ruff kapsamı dışında.

## Komutlar

```bash
# Kurulum
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Kontroller (her değişiklikten sonra üçü de temiz olmalı)
ruff check .
ruff format --check .
pytest

# Uygulama (sahte servisle)
USE_MOCK=1 streamlit run app.py              # macOS/Linux
$env:USE_MOCK="1"; streamlit run app.py      # Windows PowerShell
```

## Testler

- `tests/conftest.py`, `USE_MOCK=1` ayarlar. Testler her zaman sahte servisle çalışır.
- Testler `data/` veya `models/` klasörüne ihtiyaç duymamalı, çünkü bu klasörler CI'da yok. Veritabanı gereken testler `tmp_path` altında geçici bir veritabanı kullanır.
- Ortam değişkenini değiştirip `src.core.api` modülünü yeniden yükleyen bir test, işi bitince modülü sahte servise geri döndürmelidir.
- Streamlit `AppTest` kullanılırken uygulama yolu mutlak verilir ve `default_timeout=30` kullanılır. Varsayılan 3 saniye soğuk başlangıçta yetmiyor.

## Git

- Dal adları: `feature/<alan>-<kisa-ad>`, `fix/<kisa-ad>`, `docs/<kisa-ad>`. `<alan>`: `ui`, `db`, `ml`, `core`.
- Commit mesajı biçimi: `tür(alan): kısa açıklama`. Açıklama Türkçe ve emir kipinde olur. Türler: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- Küçük, mantıklı commit'ler at. Her commit'te ruff ve pytest temiz kalmalı.
- `main` dalına doğrudan commit atma. Force push yapma. Açıkça istenmedikçe push etme.

## Görevi bitirirken

1. `ruff check .`, `ruff format --check .` ve `pytest` komutlarını çalıştır, üçü de temiz olmalı.
2. Kısa bir rapor yaz: yapılanlar, oluşturulan ve değişen dosyalar, commit listesi, kabul komutlarının çıktısı, açık sorular.
3. Bir şey belirsizse tahmin yürütme: dur ve sor.
