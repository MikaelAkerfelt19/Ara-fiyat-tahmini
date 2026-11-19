# Doğrulama Kaydı — ARAYUZ_KONSEPT.md §12

**Tarih:** 19 Kasım 2026 · **Commit:** `git log -1` ile görülebilir son sürüm · **Ortam:** temiz klon + gerçek DB/model

Aşağıdaki maddeler "tahmin" değil, çalıştırılmış komut ve tarayıcı testi ile **doğrulanmıştır**.

| # | Kontrol maddesi | Durum | Kanıt |
|---|---|---|---|
| 1 | Sahte servis kapalıyken gerçek veriyle açılıyor ve tahmin veriyor | ✅ | `env -u USE_MOCK streamlit run app.py` + Playwright: Toyota Corolla 2015 / 100.000 km → **1.262.707 ₺**, aralık 791.085 ₺ – 1.901.453 ₺. `docs/img/sonuc.png` |
| 2 | §5'teki her durum denendi, hiçbirinde traceback görünmüyor | ✅ | `tests/test_davranis.py` + `tests/test_app.py`: 11 senaryo, her birinde `at.exception == []` |
| 3 | §6'daki tasarım ilkelerinin hepsi sağlanıyor | ✅ | `tests/test_tasarim.py` (4 test) + `.streamlit/config.toml` + `docs/img/telefon.png` |
| 4 | Kodda sabit yazılmış seçenek veya sınır yok | ✅ | `app.py` tüm seçenekleri `service.get_options()`'tan okur; statik fallback `src/app/options.py` silindi. Sabit veri yalnızca sahte servistedir (CONTRACT.md §5 bunu açıkça tanımlar) |
| 5 | `pytest` geçiyor, `ruff check .` temiz | ✅ | `28 passed` · `ruff check .` → *All checks passed* · `ruff format --check .` temiz |
| 6 | Ekran görüntüleri ve README güncel | ✅ | 4 PNG gerçek servisle yeniden üretildi; README gerçek CSV kurulumu, 168.365 ilan ve MAE 4.315 $ / R² 0,799 ile güncellendi |
| 7 | Commit geçmişinde senin adınla düzenli commit'ler var | ✅ | 18 commit; son 10'u `meng-IO <osmanUniversite1@gmail.com>` (ilk 8'i yerel yazar ayarı öncesi `meng-git`) |
| 8 | Canlı demo provası yapıldı | ✅ | Playwright uçtan uca: form doldur → tahmin → geçmiş → model bilgisi → telefon genişliği; ekran görüntüleri kanıt |

## §5 durumlarının karşılığı

| Durum | Test / kanıt |
|---|---|
| Sayfa ilk açıldığında seçenekli alanlar boş, sayı alanları makul | `test_sayfa_hatasiz_acilir`, `test_ilk_acilis_durumu` |
| Marka seçilmeden model kapalı, "Önce marka seçin" | `test_marka_degisince_model_sifirlanir`, `test_ilk_acilis_durumu` |
| Marka seçilince yalnızca o markanın modelleri | `test_marka_degisince_model_sifirlanir` |
| Marka değişince önceki model temizlenir | `test_marka_degisince_model_sifirlanir` |
| Sayı sınırları servisten | `service.get_ranges()` → yıl/km seçenekleri DB'den |
| Eksik alanla buton → sarı uyarı, servis çağrılmaz | `test_eksik_alan_servis_cagrilmaz` |
| Hesaplanıyor göstergesi | `st.spinner("Hesaplanıyor…")` (kod + canlı prova) |
| Başarılı tahmin → sonuç + geçmişe kayıt | `test_tam_formda_sonuc_gorunur`, `test_son_tahminler_en_yeni_ustte` |
| Sonra başka alana dokununca sonuç kalır | `test_sonuc_baska_alana_dokununca_kalir` |
| Model hazır değil → anlaşılır mesaj | `test_model_hazir_degil` |
| Geçersiz girdi → servis mesajı kırmızı kutuda | `test_gecersiz_girdi_mesaji_gosterilir` |
| Beklenmeyen hata → kullanıcıya traceback yok | `test_beklenmeyen_hata_traceback_vermez` |
| Henüz tahmin yok → "Henüz tahmin yapılmadı." | `test_render_history_bos`, `test_ilk_acilis_durumu` |
| Model bilgisi yok → "Model bilgisi henüz yok." | `test_render_model_info_yok`, `test_ilk_acilis_durumu` |

## Gerçek veri doğrulaması

```
python -m src.db.load_data
  Kaggle: 784 → 652 satır
  vehicles: 295451 → 167730 → (sızıntı 17) 167713 satır
  cars tablosu yazıldı: 168365 satır {'vehicles': 167713, 'kaggle': 652}

python -m src.ml.train
  5 katlı CV: MAE=4315  RMSE=8817  R²=0.799  medyan % hata=19.5%
  model_version: 20261119-0308
  referans araç sapmaları: çoğu %3'ten az; en yüksek RAV4 +%27,5
```

Servis çıktısı (gerçek mod): 48 marka, 78 yıl (1950–2027), 91 km seçeneği, Toyota için 29 model, `Prediction(currency="TRY", usd_try=50.4444)`.

Marka listesi, model listesiyle **aynı eşiği** kullanır: yalnızca en az 20 ilanı olan
modeli bulunan markalar gösterilir. Böylece veride 4 ilanı ve çöp model adları
(`Diesel`, `Rows`, `4X4`, `Passenger`) olan **Seat** gibi markalar açılır listede
yer almaz; kullanıcı boş model listesiyle karşılaşmaz. Doğrulama:
`[b for b in options["brand"] if not service.get_models_for_brand(b)] == []`.

## Not

`get_options()` fonksiyonuna eklenen `year` ve `mileage` anahtarları CONTRACT.md'deki imzayı genişletir.
Belge güncellemesi ve iki kişilik onay (Kaan) hâlâ bekleniyor; bu, §12 maddelerinden bağımsız bir süreç maddesidir.

## V2 ek doğrulamaları (osman/frontend-v1 üzerine)

| Kontrol | Sonuç |
|---|---|
| Arka plan açık gri-mavi (`#F4F7FB`) | ✅ tarayıcıda `rgb(244,247,251)` doğrulandı |
| Marka seçilmeden Model görünmüyor | ✅ 1 selectbox ("Marka"), "Önce marka seçin" yazısı |
| Model seçilmeden yıl/km/yakıt/vites/diğer alanlar gizli | ✅ 2 selectbox (Marka + Model), `number_input` yok |
| Silindir: Elektrik ve Hibrit'te gizli, Dizel'de görünür | ✅ Playwright + 3 parametreli test |
| Sonuçta dolar/TL dönüşüm satırı yok | ✅ backend fiyatı TL döndürüyor, arayüz sadece TL gösteriyor |
| Testler | **137 passed** (103 backend + 34 frontend) |
| ruff check / format --check | temiz |
| Ekran görüntüleri | gerçek servisle yeniden üretildi (`docs/img/*.png`) |

Veri ve fiyatlar Kaan'ın backend'i (`src.core.service` → `data/cars.db` + model) üzerinden
geliyor; arayüz veritabanına/model dosyasına doğrudan erişmiyor.
