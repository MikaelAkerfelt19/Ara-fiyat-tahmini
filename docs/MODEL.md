# Model Deney Günlüğü

> Sorumlu: Kaan · Durum: **Şablon** (Rehber Adım 5'ten itibaren doldurulur)

## 1. Değerlendirme düzeni

- Doğrulama: `train.csv` verisinin %20'si ayrılır (`random_state=42`). Model bu kısmı eğitimde hiç görmez.
- Çapraz doğrulama: 5 katlı `KFold` (Adım 8'den itibaren)
- Ana metrik: **MAE** (ortalama mutlak hata, para birimi cinsinden; anlaması en kolay olan)
- Ek metrikler: RMSE, R²
- Yarışma metriği: `____` (DATA.md §1)

## 2. Deneyler

Her denemeyi bir satır olarak ekle, kötü sonuç verenleri de. Neyin işe yaramadığı da bir bulgudur.

| # | Tarih | Model | Özellikler / değişiklik | Önemli parametreler | MAE | RMSE | R² | Not |
|---|---|---|---|---|---|---|---|---|
| 0 | | Baseline (medyan) | – | – | | | | Geçilmesi gereken çizgi |
| 1 | | Ridge + one-hot, log hedef | | `alpha=1.0` | | | | |
| 2 | | RandomForest | | | | | | |
| 3 | | HistGradientBoosting | | | | | | |
| 4 | | HistGradientBoosting (ayarlı) | | | | | | |

## 3. Seçilen model

- Model: `____`
- Parametreler: `____`
- Doğrulama sonuçları: MAE `____` · RMSE `____` · R² `____`
- Baseline'a göre iyileşme: MAE'de `%____`
- Neden bu model: _(2–3 cümle)_

## 4. Özellik önemleri

_(Adım 10: permutation importance grafiği `docs/img/ozellik_onemi.png` ve kısa yorum)_

## 5. Hata analizi

_(Adım 10: model en çok nerede yanılıyor? Hangi marka, fiyat aralığı veya yaşta?)_

## 6. Kaggle sonucu (bonus)

| Tarih | Model sürümü | Public skor | Not |
|---|---|---|---|
| | | | |
