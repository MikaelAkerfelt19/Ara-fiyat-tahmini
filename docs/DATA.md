# Veri Sözlüğü

> Sorumlu: Kaan · Doldurulma zamanı: Rehber Adım 1–3 (Hafta 1) · Durum: **Dolduruldu (16 Kasım 2026)**

## 1. Kaynak

- Yarışma: Kaggle, *Used Car Price Prediction Challenge*
- Bağlantı: https://www.kaggle.com/competitions/used-car-price-prediction-challenge
- Açıklama: Craigslist ABD ilanlarından toplanmış ikinci el araç verisi. Görev regresyon (sayısal fiyat tahmini).
- Değerlendirme metriği (Overview → Evaluation): Kaggle Overview → Evaluation'dan bakılacak
- Lisans / kullanım kuralı (Rules sekmesi): Kaggle Rules sekmesinden bakılacak

## 2. Dosyalar

| Dosya | Satır | Sütun | Açıklama |
|---|---|---|---|
| `train_data_v2.csv` | 784 | 28 | Fiyatı bilinen ilanlar (eğitim) |
| `test_data_v2.csv` | 278 | 27 | Fiyatı olmayan ilanlar (Kaggle tahmini için) |
| `sample_submission.csv` | 278 | 2 | Gönderim formatı (`ID`, `price`) |

## 3. Hedef değişken

- Sütun adı: `price`
- Para birimi: USD
- Min / medyan / max: 0 / 9.500 / 5.771.710
- Dağılım: Çok sağa çarpık (çarpıklık yaklaşık 27,6); birkaç aşırı uç değer var. Log dönüşümü modelleme aşamasında denenecek. Hatalı ve uç fiyatlar `filter_train_rows()` ile eğitimden çıkarılır (§6).

## 4. Sütunlar

"Ham ad" CSV'deki adıdır. "Temiz ad" ise kodda ve veritabanında kullanılacak ad. "—" temiz adı olmayan, kullanılmayan sütundur.

| Ham ad | Temiz ad | Ham tür | Temiz tür | Eksik % | Benzersiz | Örnek değerler | Temizlik kararı | Modelde? |
|---|---|---|---|---|---|---|---|---|
| ID | id | int | int | 0 | 784 | 1, 2, 3 | Olduğu gibi | Hayır (kimlik) |
| condition | condition | metin | Türkçe etiket | 36,2 | 6 | like new, good, excellent | Türkçe etikete eşlenir | Evet |
| cylinders | cylinders | metin | Int64 | 29,5 | 8 | 3 cylinders, 4 cylinders | Sayı çıkarılır, "other" boş | Evet |
| drive | drive | metin | Türkçe etiket | 35,3 | 3 | 4wd, rwd, fwd | Türkçe etikete eşlenir | Evet |
| engine | — | metin | — | 89,4 | 73 | 6-Cyl, V6 | Çıkarıldı (neredeyse boş) | Hayır |
| est._monthly_pmt | — | metin | — | 99,7 | 1 | $1 | Çıkarıldı (boş/çöp) | Hayır |
| ext_color | — | metin | — | 99,2 | 6 | Gray Int Color... | Çıkarıldı (boş/çöp) | Hayır |
| feature_count | — | int | — | 0 | 1 | 1 | Çıkarıldı (sabit) | Hayır |
| features_list | — | metin | — | 0 | 767 | QR Code Link... | Çıkarıldı (serbest metin) | Hayır |
| fuel | fuel_type | metin | Türkçe etiket | 0,1 | 5 | gas, hybrid, diesel | Türkçe etikete eşlenir | Evet |
| image_count | — | int | — | 0 | 24 | 4, 7, 13 | Çıkarıldı (kullanıcı giremez) | Hayır |
| int_color | — | metin | — | 99,2 | 6 | Brown Power Door... | Çıkarıldı (boş/çöp) | Hayır |
| make | — | metin | — | 90,2 | 76 | *Ford** Model... | Çıkarıldı; marka `title`'dan | Hayır |
| mileage | — | metin | — | 88,4 | 72 | 288, 247, 117 | Çıkarıldı (boş); km `odometer`'dan | Hayır |
| model | — | metin | — | 91,2 | 69 | *Ranger** Series... | Çıkarıldı; model `title`'dan | Hayır |
| odometer | mileage | float | Int64 (km) | 1,8 | 597 | 60700, 288977 | Mil → km, aşırı değerler boş | Evet |
| paint_color | — | metin | — | 26,9 | 12 | grey, white, blue | Çıkarıldı (zayıf sinyal) | Hayır |
| price | price | int | int (USD) | 0 | 366 | 18500, 3999 | Hedef değişken | Hedef |
| scrape_timestamp | — | metin | — | 0 | 784 | 2026-06-23T20:52:06 | Çıkarıldı (veri toplama zamanı) | Hayır |
| search_price | — | float | — | 100 | 0 | – | Çıkarıldı (tamamen boş) | Hayır |
| title | year, brand, model | metin | int, metin, metin | 0 | 769 | 2021 Ford Bronco Sport | `parse_title()` ile ayrıştırılır | Evet |
| title_status | title_status | metin | Türkçe etiket | 1,0 | 6 | clean, salvage, missing | Türkçe etikete eşlenir (salvage → "Ağır hasarlı", rebuilt → "Ağır hasarlı (onarılmış)") | Evet |
| trans | — | metin | — | 95,7 | 21 | Auto, Automatic | Çıkarıldı (neredeyse boş) | Hayır |
| transmission | transmission | metin | Türkçe etiket | 1,4 | 3 | automatic, other, manual | Türkçe etikete eşlenir | Evet |
| trim | — | metin | — | 91,7 | 59 | 740i Sedan 4D... | Çıkarıldı (neredeyse boş) | Hayır |
| type | body_type | metin | Türkçe etiket | 10,8 | 13 | SUV, truck, coupe | Türkçe etikete eşlenir | Evet |
| vin | — | metin | — | 60,3 | 311 | 1FTYR10DX4PA... | Çıkarıldı (benzersiz kimlik) | Hayır |
| year | — | metin | — | 90,7 | 73 | 2004* Make... | Çıkarıldı; yıl `title`'dan (yedek: ham yılın ilk 4 hanesi) | Hayır |

## 5. Temizlik kararları günlüğü

| # | Karar | Neden | Etkilenen satır |
|---|---|---|---|
| 1 | Marka, model ve yıl `title` sütunundan ayrıştırıldı | Ham `make`/`model`/`year` sütunları %90'dan fazla boş; `title` her satırda dolu | Tümü |
| 2 | Açık marka listesi + yalnızca tam eşleşen takma adlar (chevy, vw…) kullanıldı | Benzerlik eşleşmesi yanlış marka atar. Chery ile Chevrolet farklı markalardır; bu yüzden yalnızca tam kelime eşleşmesi kullanılır. Marka ilk 4 kelimede aranır; böylece "John Deere … Mini excavator" Mini sayılmaz | Marka bulunamayan satırlar boş kalır (%5,2) |
| 3 | `odometer` mil → km çevrildi (× 1,609344) | Veri mil cinsinden; arayüz ve sözleşme km kullanır | Tümü |
| 4 | 1.600.000 km üstü veya ≤ 0 kilometre boş yapıldı | Girdi hatası; satır silinmez, değer boş kalır | Birkaç satır |
| 5 | Kategori değerleri Türkçe etiketlere eşlendi; eşlemede olmayan değer boş | Arayüz Türkçe gösterir; bilinmeyen değerler sessizce karışmaz | Tümü |
| 6 | `cylinders` metninden sayı çıkarıldı | Model sayısal değeri okur; "other" belirsiz olduğu için boş | %29,5 boş |
| 7 | `paint_color` çıkarıldı | Fiyata zayıf sinyal; arayüzü gereksiz uzatır | – |
| 8 | `image_count` çıkarıldı | Kullanıcı arayüzde giremez | – |
| 9 | Boş/çöp/sabit sütunlar çıkarıldı (engine, trans, trim, ext_color, int_color, est._monthly_pmt, search_price, feature_count, features_list, vin, scrape_timestamp) | Neredeyse boş, sabit, serbest metin veya kimlik niteliğinde | – |
| 10 | `clean()` satır silmez; filtreler yalnızca eğitimde `filter_train_rows()` içinde | Test verisi aynı biçimde işlenebilmeli | – |
| 11 | Model adlarından tire kaldırıldı, "Range Rover" gibi iki kelimelik adlar birleştirildi, markanın tekrarı atlandı | "F-150" ile "F150" aynı araç; model sayısı azalır, her modelde daha çok örnek olur | Tümü |
| 12 | Model adındaki tek harf sonraki kelimeyle bitişik yazıldı ("C 250" → "C250", "G 35" → "G35"); rakamla başlayanlar ("3 Series") ve "Model 3" gibi adlar boşluklu kaldı | Veride "C 250" ile "C250" aynı araç; model sayısı azalır | Tek harfli model adları |
| 13 | `title_status` etiketleri: salvage "Ağır hasarlı", rebuilt "Ağır hasarlı (onarılmış)" | Türkiye'de onarılmış araç da ağır hasar kayıtlı sayılır; "pert" yerine yaygın terim kullanılır | title_status dolu satırlar |
| 14 | `seller_type` ("Galeri" / "Bireysel") eklendi. Kaggle'da etiket yok: `features_list` + `title` metninde galeri kalıbı (`DEALER_PATTERN`) aranır; vehicles'ta gerçek `seller_type` sütunu kullanılır | Galeri ve bireysel fiyatı farklıdır; kalıp vehicles etiketine karşı sınandı (%86 doğru, bkz. §8) | Tümü |
| 15 | Başlıktan marka çıkmazsa vehicles `manufacturer` sütunu yedek olur ("rover" → Land Rover) | Başlıkta marka olmayan ilanlar boşa gitmesin; satır silinmez | vehicles |
| 16 | `odometer_broken` / `odometer_rolled_over` = 1 ise km boş yapılır | Bozuk sayaç km'si yanıltıcıdır; satır silinmez, eğitimde "km yok" kuralıyla elenir | vehicles |
| 17 | Çıktıya `title` sütunu eklendi (veritabanına yazılmaz) | İki set arasında aynı ilanı bulmak (sızıntı kontrolü, §8) | Tümü |
| 18 | Eski %0,5 / %99,5 fiyat yüzdelik kuralı kaldırıldı; yerine sabit çöp kuralları (§6) | Yüzdelik, verinin ne kadar kirli olduğuna bağlıdır ve iyi ilanları da keser; sabit kurallar açıklanabilir | Eğitim |

## 6. Eğitimden çıkarılan satırlar

`filter_train_rows()` içinde uygulanır. **Test verisine uygulanmaz.** Kurallar sırayla çalışır; her satır, öncekilerden **kalan** satırlar üzerinden sayılır. Sayıları `python -m src.db.load_data` yazdırır (`filter_report()`).

| Kural | Neden | Kaggle (784) | vehicles (295.451) |
|---|---|---|---|
| Marka bulunamayan | Araç olmayan ilan (bisiklet, ekskavatör, reklam) | 40 | 4.453 |
| Fiyat 1.000 $ altı | Peşinat, "ara" ilanı, tek haneli fiyat; gerçek satış fiyatı değil | 6 | 14.409 |
| Fiyat 250.000 $ üstü | Çoğunlukla fazladan yazılmış sıfır | 0 | 212 |
| Yıl 1950 öncesi veya yok | Yıl en güçlü özellik; koleksiyon araçları ayrı bir piyasa | 62 | 903 |
| Km yok, 600.000 üstü veya bozuk sayaç | İkinci en güçlü özellik eksik ya da güvenilmez | 13 | 7.620 |
| 2.000 km altı ama 2024 öncesi | Eski araçta bu km sayaç sıfırlanması / girilmemiş değerdir (sahte km) | 10 | 2.029 |
| "Parça için" ruhsat | Çalışan araç fiyatını bozar | 1 | 55 |
| Tekrar ilan (marka, model, yıl, km, fiyat aynı) | Aynı ilan birden çok kez girilmiş | 0 | 98.042 |
| **Kalan** | | **652** | **167.728** |

Kaggle ilanlarıyla (başlık, fiyat) çakışan 17 ilan ayrıca vehicles'tan çıkarılır (§8); eğitimde 167.711 vehicles ilanı kalır.

## 7. EDA'dan öne çıkanlar

Grafikler `docs/img/` altında, kodu `notebooks/02_eda.ipynb` içindedir.

- (Bu bölümdeki sayılar eski filtreyle, 771 ilan üzerinden alındı; yeni filtre 652 ilan bırakır.) Temizlik sonrası 771 ilan var. Fiyat medyanı 9.500 USD, ortalaması yaklaşık 15.287 USD; dağılım hâlâ sağa çarpık (çarpıklık yaklaşık 3,2). Log dönüşümü dağılımı dengeliyor (`fiyat_dagilimi.png`).
- Model yılı ile fiyat arasında güçlü pozitif ilişki var (Spearman yaklaşık 0,56); yeni araçlar pahalı (`yil_fiyat.png`).
- Kilometre ile fiyat ters ilişkili (Spearman yaklaşık -0,53); yıl ile kısmen aynı bilgiyi taşır (`km_fiyat.png`).
- Marka fiyatı belirgin etkiler: en sık 15 marka içinde medyan Tesla yaklaşık 27.950 USD, Chevrolet yaklaşık 14.950 USD, BMW yaklaşık 14.250 USD; Nissan yaklaşık 5.050 USD (`marka_medyan_fiyat.png`).
- Eksik değer oranları yüksek: condition %36, drive %35, cylinders %32, body_type %11, year %10. Bu yüzden ön işlemede imputer ve "Bilinmiyor" sınıfı kullanılıyor.
- İlanların çoğu Toyota (96), Ford (94), Chevrolet (74) ve BMW (58); diğer markalarda örnek az olduğundan marka etkisi gürültülü olabilir.

## 8. İkinci veri seti: vehicles.csv

**Kaynak:** Craigslist ABD ikinci el araç ilanları, eylül-kasım 2026 (`data/raw/vehicles.csv`, yaklaşık 1,1 GB, 295.451 ilan). Dosya isteğe bağlıdır: yoksa sistem yalnız Kaggle verisiyle çalışır. Repoya girmez.

**Neden:** Kaggle verisi yalnızca 652 temiz ilan içerir; 5 katlı ölçümde yalnız Kaggle ile MAE 6.139 $, R² 0,485 çıktı. Aynı 652 ilan üzerinde Kaggle + vehicles (Kaggle ağırlığı 5) ile MAE 4.345 $, R² 0,792 oldu.

**Sütun eşlemesi** (yalnızca gereken 16 sütun okunur, `description` okunmaz):

| vehicles sütunu | Temiz ad | Not |
|---|---|---|
| `id` | `id` | `ID`'ye çevrilip `clean()`'e verilir |
| `price` | `price` | USD |
| `title` | `year`, `brand`, `model` | Kaggle ile aynı `parse_title()`; ayrıca `title` sızıntı kontrolü için kullanılır |
| `year` | `year` | Başlıkta yıl yoksa yedek |
| `manufacturer` | `brand` | Başlıktan marka çıkmazsa yedek ("rover" → Land Rover) |
| `odometer` | `mileage` | Mil → km |
| `odometer_broken`, `odometer_rolled_over` | – | 1 ise km boş yapılır |
| `condition`, `cylinders`, `fuel`, `transmission`, `drive`, `type`, `title_status` | Kaggle ile aynı | Aynı Türkçe etiketlere eşlenir |
| `seller_type` | `seller_type` | dealer → "Galeri", owner → "Bireysel" |

**Satıcı tipi:** vehicles'ta gerçek etiket var. Kaggle'da yok; ilan metninde `DEALER_PATTERN` (dealer, financ, credit, stock #, warrant, offered by, carfax) aranır. Kalıp vehicles'ta (etiketi bilinen 40.000 ilan) ilanların **%86'sında** doğru sonucu verdi. Yani Kaggle'daki "Galeri" etiketi kusurlu ama işe yarar bir tahmindir.

**Çöp kuralları:** §6'daki tabloda iki set yan yana. vehicles'ta ilanların 98.042'si tekrar (aynı marka, model, yıl, km, fiyat); yani aynı ilan çok kez girilmiş. Çöp temizliğinden sonra 167.728 ilan kalır.

**Sızıntı temizliği:** Ölçümü Kaggle ilanları üzerinde yaptığımız için, aynı ilan vehicles'ta da varsa model cevabı eğitimde görmüş olur. (Başlık, fiyat) çifti Kaggle ile eşleşen ilanlar vehicles'tan çıkarılır: süzülmemiş Kaggle ilanlarından 23'ü vehicles'ta da vardı; çöp temizliğinden sonra vehicles'tan 17 ilan çıkarıldı (167.728 → 167.711).

**Veritabanı:** `cars` tablosuna `seller_type` ve `source` ("kaggle" / "vehicles") sütunları eklendi; toplam 168.363 satır (652 + 167.711). `brand` ve `brand+model` üzerinde indeks vardır.

**Dağılım farkı:** vehicles'ın medyan fiyatı Kaggle'dan yüksektir (ham veride 12.500 $ ve 9.500 $) ve ilanların %73,9'u galeri (Kaggle'da metin tahminiyle %46). Bu yüzden Kaggle ilanları eğitimde 5 kat ağırlık alır (`KAGGLE_WEIGHT`).

