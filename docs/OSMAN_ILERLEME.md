# İlerleme Kaydı (19 Kasım 2026)

Bu dosya oturum kapatıldığında bile projenin nerede olduğunu gösterir.
Ayrıntılı doğrulama kanıtları: [`DOGRULAMA.md`](DOGRULAMA.md).

## Kararlar

- Fiyat birimi **TL**, gösterim **`₺`**.
- Form 12 alan: 6 zorunlu + 6 isteğe bağlı.
- Marka, model, yıl ve kilometre seçenekleri **doğrudan `cars` tablosundan** gelir.
- Fiyatlar servisten TL olarak gelir; arayüz dolar/TL dönüşümünü göstermez.
- Git yazarı bu repo için `meng-IO` (son 10 commit); GitHub remote **yok**.

## Adımlar ve commit'ler

| # | Commit | Açıklama |
|---|---|---|
| 1 | `de4dd5a` | Ortam: git init, `.gitignore`, venv, sabit bağımlılıklar, iskelet |
| 2 | `5623953` | `src/core/`: şema, hata, sahte servis, API seçimi |
| 3 | `a305f62` | Sayfa iskeleti, tema, fiyat biçimlendirme + test |
| 4 | `739bce2` | Tahmin formu, seçenek/sınırlar servisten |
| 5 | `75704c2` | Markaya bağlı model listesi ve sıfırlama |
| 6 | `e22119c` | Doğrulama ve kullanıcı dostu hata mesajları |
| 7 | `df0829d` | Sonuç bölümü, session state ile kalıcılık |
| 8 | `0d452a6` | Son tahminler tablosu |
| 9 | `4c8acdd` | README'ye uyarlama: TL ve 12 alan |
| 10 | `0b6a60d` | Model hakkında bölümü, USD metrik notu |
| 11 | `78d42c3` | Önbellek ve metin tutarlılığı |
| 12 | `8b4ffaf` | Gerçek servise geçişte güvenli fallback, aranabilir listeler |
| 13 | `c790397` | README, güncel sözleşme, ekran görüntüleri, 19 test |
| 14 | `1d17891` | Oturum kapanmadan önce ilerleme kaydı |
| 15 | `6e1b826` | Gerçek temizleme kodu + seçenekli yıl/km |
| 16 | `fae3173` | 70 gerçek marka, 411 model (mock veri) |
| 17 | `3bc8ef3` | Seçenekler DB'den, gerçek servis bağlandı |
| 18 | `388aeea` | `localization.json` repoya girmesin |
| 19+ | (son commit) | §12 doğrulama: §5/§6 testleri, sabit seçenek kaldırıldı, gerçek ekran görüntüleri, README/DOGRULAMA |

## Son durum

- `pytest` → **28 passed** · `ruff check .` ve `ruff format --check .` temiz.
- Veri: `data/cars.db` → **168.365 satır** (652 Kaggle + 167.713 vehicles).
- Model: `models/model.joblib` sürüm `20261119-0308`, MAE 4.315 $, R² 0,799.
- Uygulama **USE_MOCK olmadan** `http://localhost:8501` adresinde çalışıyor.
- Gerçek örnek tahmin: Toyota Corolla 2015 / 100.000 km → **1.262.707 ₺**.
- Ekran görüntüleri gerçek veriyle yenilendi (`docs/img/`).

## Yerel konumlar

- Geliştirme reposu: `~/Desktop/git-directory/Python/arabam-git/arayuz-paketi`
- Temiz klon: `~/Desktop/arayuz-sifir-local` (veri + model kopyalandı, 28 test geçiyor)

## Sıradaki adım: GitHub'a bağlanma

Kullanıcı "GitHub'a bağlanmak istiyorum" dediğinde:

1. GitHub'da **boş** repo oluştur (README/LICENSE ekleme).
2. Geliştirme reposunda:
   ```bash
   git remote add origin <VERILEN_GITHUB_ADRESI>.git
   git switch -c feature/ui-gercek-servis
   git push -u origin feature/ui-gercek-servis
   ```
3. PR aç: ne değişti / nasıl test edildi / ekran görüntüsü / `Closes #A9`.
4. Kaan inceleyip **merge commit** ile birleştirir (squash yok).
5. Ayrıca: `get_options()` uzantısı için CONTRACT.md güncellemesi ve iki kişilik onay gerekir.
