# Veri Sözlüğü

> Sorumlu: Kaan · Doldurulma zamanı: Rehber Adım 1–3 (Hafta 1) · Durum: **Şablon**

## 1. Kaynak

- Yarışma: Kaggle, *Used Car Price Prediction Challenge*
- Bağlantı: https://www.kaggle.com/competitions/used-car-price-prediction-challenge
- Açıklama: İnternetteki ilan sitelerinden toplanmış gerçek ikinci el araç verisi. Görev regresyon (sayısal fiyat tahmini).
- Değerlendirme metriği (Overview → Evaluation): `____` _(RMSE, MAE, RMSLE…)_
- Lisans / kullanım kuralı (Rules sekmesi): `____`

## 2. Dosyalar

| Dosya | Satır | Sütun | Açıklama |
|---|---|---|---|
| `train.csv` | | | Fiyatı bilinen ilanlar (eğitim) |
| `test.csv` | | | Fiyatı olmayan ilanlar (Kaggle tahmini için) |
| `sample_submission.csv` | | | Gönderim formatı |

## 3. Hedef değişken

- Sütun adı: `____`
- Para birimi: `____`
- Min / medyan / max: `____ / ____ / ____`
- Dağılım: _(çarpık mı? log dönüşümü sonrası nasıl?)_

## 4. Sütunlar

"Ham ad" CSV'deki adıdır. "Temiz ad" ise kodda ve veritabanında kullanılacak ad: küçük harf, alt çizgili, İngilizce.

| Ham ad | Temiz ad | Ham tür | Temiz tür | Eksik % | Benzersiz | Örnek değerler | Temizlik kararı | Modelde? |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |
| | | | | | | | | |
| | | | | | | | | |

## 5. Temizlik kararları günlüğü

Her kararı **neden** verdiğinle birlikte yaz. Sunumda sorulursa buradan cevap verirsin.

| # | Karar | Neden | Etkilenen satır |
|---|---|---|---|
| 1 | | | |

Örnek satır: `Kilometre "120,000 km" metninden sayıya çevrildi` · `Model sayısal olmayan değerleri okuyamaz` · `Tümü`

## 6. Eğitimden çıkarılan satırlar

`filter_train_rows()` içinde uygulanır. **Test verisine uygulanmaz.**

| Kural | Çıkarılan satır | Kalan satır |
|---|---|---|
| Tamamen aynı (tekrar) satırlar | | |
| Fiyat uç değerleri (%0,5 altı ve %99,5 üstü) | | |

## 7. EDA'dan öne çıkanlar

_(Adım 3 sonunda 4–6 madde: en çok fiyatı etkileyen görünen özellikler, ilginç ilişkiler, şüpheli değerler)_

-
