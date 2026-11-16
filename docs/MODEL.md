# Model Deney Günlüğü

> Sorumlu: Kaan · Durum: **Dolduruldu** (16 Kasım 2026)

## 1. Değerlendirme düzeni

- Doğrulama: `train.csv` verisinin %20'si ayrılır (`random_state=42`). Model bu kısmı eğitimde hiç görmez.
- Çapraz doğrulama: 5 katlı `KFold` (Adım 8'den itibaren)
- Ana metrik: **MAE** (ortalama mutlak hata, para birimi cinsinden; anlaması en kolay olan)
- Ek metrikler: RMSE, R²
- Veri az (771 satır) olduğu için model seçimi **5 katlı CV MAE** ile yapılır; holdout (%20 = 155 satır) ek bilgidir ve tek bölme gürültülüdür.
- Yarışma metriği: `____` (DATA.md §1)

## 2. Deneyler

Her denemeyi bir satır olarak ekle, kötü sonuç verenleri de. Neyin işe yaramadığı da bir bulgudur.

| # | Tarih | Model | Özellikler / değişiklik | Önemli parametreler | MAE | RMSE | R² | Not |
|---|---|---|---|---|---|---|---|---|
| 0 | 16 Kas 2026 | Baseline (medyan) | – | – | 9094 / CV 10084 | 15966 / CV 17857 | -0,123 / CV -0,120 | Geçilmesi gereken çizgi |
| 1 | 16 Kas 2026 | Ridge + one-hot, log hedef | Ölçekli sayısal | `alpha=1.0` | 7442 / CV 7305 | 13948 / CV 14056 | 0,143 / CV 0,304 | Doğrusal ilişki yetersiz |
| 2 | 16 Kas 2026 | RandomForest | One-hot, log hedef | `n_estimators=300` | 5854 / CV 6048 | 12400 / CV 12516 | 0,323 / CV 0,448 | Holdout'ta en iyi varsayılan |
| 3 | 16 Kas 2026 | HistGradientBoosting | One-hot, log hedef | varsayılan | 5966 / CV 6028 | 12576 / CV 12182 | 0,303 / CV 0,475 | CV'de en iyi varsayılan |
| 4 | 16 Kas 2026 | HistGradientBoosting (ayarlı) | RandomizedSearchCV, 15 deneme | bkz. §3 | 5445 / CV 5881 | 11855 / CV 12123 | 0,381 / CV 0,481 | Monoton kısıt eklenmeden önceki en iyi |
| 5 | 16 Kas 2026 | HistGB ayarlı + monoton kısıt (km −, yıl +) | `monotonic_cst={"num__mileage": -1, "num__year": 1}`, #4 parametreleri | – / CV 6120 | – / CV 12653 | – / CV 0,447 | Seçilen model; MAE ~%4 kötüleşti, karşılığında km ve yıl eğrisi tutarlı |

Her hücre "holdout / CV ortalaması" biçimindedir. MAE ve RMSE USD cinsindendir. CV MAE standart sapmaları: Ridge 551, RF 589, HistGB 792, ayarlı HistGB 808.

## 3. Seçilen model

- Model: `HistGradientBoostingRegressor` (log1p hedef, one-hot ön işleme, km için azalan ve yıl için artan monoton kısıt; özellik adları `num__mileage` ve `num__year`)
- Parametreler: `learning_rate=0.03, max_iter=400, max_leaf_nodes=15, min_samples_leaf=5, l2_regularization=0`
- 5 katlı CV sonuçları (monoton kısıtlı): MAE `6120` · RMSE `12653` · R² `0,447` (kısıtsız ayarlı model: 5881 / 12123 / 0,481)
- Baseline'a göre iyileşme: MAE'de yaklaşık %39 (10084 -> 6120, CV)
- Neden bu model: CV MAE'si en düşük ağaç modeli HistGB oldu ve ayarlama varsayılana göre CV MAE'yi 6028'den 5881'e indirdi (küçük bir kazanç; fark standart sapma içinde, o yüzden iddialı yorumlanmamalı). Ridge, ağaç modellerinden belirgin kötüydü.
- `train.py` çıktısı (out-of-fold tahminlerle): MAE 6120 · RMSE 12653 · R² 0,447. Kısıt ağaçların esnekliğini azalttığı için metrikler biraz kötüleşti; bu bilerek kabul edildi (tutarlılık doğruluktan önceliklidir).
- Bu metrikler USD içindir; Türkiye fiyatları için ayrı bir yerel katsayı uygulanacaktır.

## 4. Özellik önemleri

![Özellik önemi](img/ozellik_onemi.png)

- Holdout üzerinde permutation importance (MAE artışı): `year` (yaklaşık 3337 USD) açık ara en önemli özellik.
- Ardından `mileage` (1411), `cylinders` (654), `brand` (452), `drive` (451) ve `fuel_type` (423) gelir.
- `model`, `transmission` ve `title_status` neredeyse sıfır veya hafif negatif önem gösterdi; küçük holdout'ta gürültü sayılır. `model` sütunu çok sayıda seyrek sınıf içerdiğinden fazla bilgi taşımıyor.
- Önem değerleri 155 satırlık holdout ve 5 tekrara dayanır, sıralama küçük farklarda değişebilir.

## 5. Hata analizi

- Marka bazında (en az 5 holdout ilanı) ortalama mutlak hata en yüksek: Mercedes-Benz 7604 USD (7 ilan), Chevrolet 6721 (14), Ford 5602 (24), Toyota 4733 (23); en düşük Hyundai 1828 (9).
- Fiyat dilimine göre medyan oransal hata U biçimli: en ucuz dilimde (1200-5000 USD) %31,6, orta dilimlerde %15-27, en pahalı dilimde (23180 USD üzeri) %31,2.
- Ucuz arabalarda küçük mutlak hata bile büyük oransal hata demektir; pahalı arabalarda ise az örnek olduğu için model zayıf.
- Holdout küçük olduğundan marka tabloları yalnızca yön gösterir; ilan sayısı az markalarda ortalamalar oynaktır.

## 6. Kaggle sonucu (bonus)

| Tarih | Model sürümü | Public skor | Not |
|---|---|---|---|
| | | | |

## 7. Türkiye uyarlaması

**Yöntem:** Model ABD verisiyle USD tahmin eder. Servis `fiyat_TL = fiyat_USD x TCMB USD/TRY kuru x katsayı` hesaplar. Katsayı eğitimden sonra, Türkiye ilan fiyatlarına bakılarak bulunur (`src/ml/localization.py`); model değişmediği için metrikler (MAE, RMSE, R²) USD olarak kalır. Kur TCMB'nin günlük dosyasından günde bir kez çekilir, internet yoksa yedek kur (50,39) kullanılır.

Referans: sahibinden/arabam.com, 16 Kasım 2026, kur 50,3942 (TCMB). Hepsi benzinli otomatik (Tesla elektrikli), temiz ruhsat. Oran = TL fiyat / (USD tahmin x kur).

| Araç | Gerçek (TL) | Sistem (TL) | Hata |
|---|---|---|---|
| Honda Civic 2017, 200.000 km | 1.250.000 | 1.088.488 | -%12,9 |
| Toyota Corolla 2011, 235.000 km | 800.000 | 590.149 | -%26,2 |
| Honda Accord 2013, 175.000 km | 900.000 | 900.000 | %0,0 |
| Toyota RAV4 2015, 165.000 km | 1.250.000 | 1.612.732 | +%29,0 |
| Jeep Wrangler 2019, 70.000 km | 4.200.000 | 4.200.000 | %0,0 |
| BMW X5 2020, 150.000 km | 3.750.000 | 3.613.024 | -%3,7 |
| Porsche Cayenne 2014, 190.000 km | 4.150.000 | 4.150.000 | %0,0 |
| Tesla Model 3 2021, 130.000 km | 2.200.000 | 2.040.945 | -%7,2 |
| Honda Civic 2020, 80.000 km | 1.750.000 | 2.009.668 | +%14,8 |
| Toyota Corolla 2019, 100.000 km | 1.400.000 | 1.897.826 | +%35,6 |
| Toyota RAV4 2021, 60.000 km | 4.100.000 | 3.177.837 | -%22,5 |
| Mercedes-Benz C200 2018, 90.000 km | 2.750.000 | 2.750.000 | %0,0 |

**Eski yöntemin sorunu (km bandı):** Km'yi sert bir 130.000 km sınırıyla iki banda ayırıp her banda ayrı katsayı vermek yanlış sonuç üretti: 2018 Corolla 120.000 km'de 1,21 M TL iken 140.000 km'de 1,99 M TL çıkıyordu; yani km arttıkça fiyat artıyordu. Neden: yüksek km'li referanslar aynı zamanda eski araçlar ve Türkiye'de eski araç değerini ABD'ye göre daha iyi koruyor. Yüksek km bandının katsayısı bu yaş etkisini de içine alıp şişti (yaş ile km karıştı).

**Yaş-km karışması bulgusu:** Referanslara regresyon uygulandığında yaş kontrol edilince km'nin kendi etkisi yalnızca yaklaşık x1,3 çıktı. Oysa modelin ABD fiyatındaki kırılması 120.000 km ile 140.000 km arasında yaklaşık x0,71 (bu çalıştırmada medyan x0,665).

**Yeni yöntem (yumuşak km çarpanı):**

`TL = km ızgarasındaki en küçük (USD tahmin x kur x taban x km çarpanı) değer, sonra x ağır hasar çarpanı`

- Rampa: `ramp_fraction(km)` 120.000 km'ye kadar 0, 140.000 km'den sonra 1, arada doğrusal. Sert sınır olmadığı için sınırda fiyat sıçramaz. Km bilinmiyorsa 1 alınır (verinin çoğunluğu yüksek km).
- Km çarpanı: `km_adjustment = exp(c x rampa)`. `c` en küçük karelerle bulunur: `log(oran) = segment kuklaları + c x rampa`. Segment kuklaları segment farkını ayırır, `c` yalnızca km etkisini ölçer.
- Üst sınır modelin kırılmasından türetilir: `c` en fazla `log(0,98 / kırılma)` olabilir (`MONOTONIC_MARGIN = 0,98`). Böylece kırılma x km çarpanı <= 0,98 olur ve km arttıkça TL fiyat yükselemez. `c` ayrıca 0'ın altına inemez (km fiyatı artırmaz). Bu çalıştırmada (monoton kısıtlı model) kırılma 0,747, km çarpanı en fazla x1,313.
- Taban: km etkisi oranlardan çıkarılır (`taban = oran / km çarpanı`), sonra geometrik ortalama alınır. Öncelik: marka+model > segment > genel.
- Segment tabanları: ekonomik 1,536 · suv 2,127 · premium 3,081 · elektrik 2,075 · genel 2,033.

**Ağır hasar kuralı:** Tapu durumu "Ağır hasarlı" veya "Ağır hasarlı (onarılmış)" ise fiyat tam x0,65 (Türkiye'de %35 daha ucuz; Kaan'ın kararı, 16 Kasım 2026). `tl_price` modele satırı "Temiz" olarak verir (model kendi küçük indirimini eklemesin), en sonda x0,65 uygular; oran tam 0,65 çıkar. `factor_for` bu çarpanı uygulamaz (çift sayım olmasın).

**Km zarfı:** `tl_price`, 0 km'den aracın km'sine kadar sabit 1.000 km adımlı ızgarada tek `predict` çağrısıyla fiyat hesaplar ve en küçüğünü alır. Aracın kendi km'si ızgaraya eklenmez; böylece km arttıkça ızgara yalnızca büyür ve fiyat her km için kesin olarak yükselmez (en fazla 1.000 km'lik yuvarlama farkı). İlk sürüm 20.000 km adım ve aracın kendi km'sini kullanıyordu; 10.000 km adımlı kontrolde 4 araçta küçük artışlar çıktı, bu yüzden değiştirildi. Doğrulama: 10 araç x 0-400.000 km (2.500 km adım) taramasında hiçbir artış yok, 400.000 km'lik tahmin 0,02 sn; 2017 Civic 150k km için yıl 2012/2015/2018/2021 fiyatları 0,91 / 1,09 / 1,53 / 1,80 M TL (azalmıyor).

**Sınırlamalar:**
- Referanslar artık birebir tutmuyor (en kötü hatalar RAV4 2015 +%28 ve RAV4 2021 -%22). Bu bilerek kabul edildi: aynı modelin düşük ve yüksek km'li iki ilanını birebir tutturmak, km arttıkça fiyatın yükselmesine yol açıyordu; tutarlılık doğruluktan önceliklidir.
- Katsayılar yalnızca 12 ilana dayanır; premium segmentte Cayenne ve X5 arasında büyük fark var, premium tabanı güvenilmezdir.
- Monotonluk: çözüldü. Model km için azalan, yıl için artan monoton kısıtla eğitilir ve `tl_price` km zarfı uygular.
- Türkiye'ye özgü ilan fiyatları (vergi, ithalat maliyeti) tek bir çarpana sıkıştırılır.
- ABD verisinde olmayan Renault, Peugeot, Togg gibi markalar tahmin edilemez.
- Kur ve piyasa fiyatları zamanla değişir; katsayılar yeniden eğitimle güncellenmelidir.
