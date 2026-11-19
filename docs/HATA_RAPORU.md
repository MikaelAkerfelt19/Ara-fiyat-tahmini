# Uçtan Uca Hata Kontrolü Raporu

**Tarih:** 19 Kasım 2026 · **Ortam:** `/home/mertmengi/Desktop/arayuz-sifir-local`
**Mod:** gerçek servis (`USE_MOCK` yok) · **Commit:** `44ab638` · **Sonuç:** ✅ PASS

## 1. Kod ve statik kontroller

| Kontrol | Sonuç |
|---|---|
| `pytest` | **30 passed** |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 31 dosya formatted |
| `python -m compileall` | hatasız |
| `git status` | temiz |
| Git'te veri/model dosyası | yok (`data/`, `models/*` ignore edilmiş) — doğru |
| HTML/CSS, sidebar, st.form taraması | yasaklı kullanım yok |

## 2. Veritabanı

| Kontrol | Sonuç |
|---|---|
| `cars` satır sayısı | **168.365** (652 Kaggle + 167.713 vehicles) |
| İndeksler | `idx_cars_brand`, `idx_cars_brand_model` var |
| Yıl / km aralığı | 1950–2027 / 2–598.676 |
| Boş marka | 0 |
| Boş model | 9.558 (ham veride model ayrıştırılamayan ilanlar; seçenek listelerine girmez) |

## 3. Seçenekler ve tutarlılık

- 48 marka, 78 yıl, 91 km seçeneği, 5 yakıt, 3 vites, 5 ruhsat durumu, 2 satıcı tipi.
- **Modeli olmayan marka: 0** — her markanın en az bir modeli var.
- `Seat` bilinçli olarak gizli: veride 4 hatalı satır var, model adları `Diesel / Rows / 4X4 / Passenger` (başlıktaki "3rd Row Seat" vb. yanlış marka sanılmış).

## 4. Servis katmanı

| Senaryo | Sonuç |
|---|---|
| `get_ranges()` | yıl 1969–2026, km 5.112–454.192, silindir 4–8 |
| `get_model_info()` | HistGradientBoosting, v20261119-0308, n=168.365, MAE 4.315 $, R² 0,799 |
| TCMB kuru | 50,4444 (18.11.2026) |
| Normal tahmin | 1.283.783 ₺, aralık içinde, `currency=TRY`, `usd_try>0` |
| Ağır hasarlı | tam **×0,65** (doğrulandı) |
| Satıcı tipi Galeri / Bireysel | 1.369.216 / 1.203.680 ₺ — hata yok |
| KM monotonluğu | 100k → 120k → 140k → 200k → 300k fiyat **hiç artmıyor** |
| Negatif km | `ValueError("Kilometre negatif olamaz.")` ✓ |
| Geçersiz yıl (1800) | `ValueError("Model yılı 1930-2027 aralığında olmalı.")` ✓ |
| Bilinmeyen marka | çökmez, makul tahmin döner |
| Geçmiş kaydı | `save_prediction` → `get_history` en yeni üstte, DB'ye yazıldı ✓ |

## 5. Tarayıcı (Playwright, gerçek servis)

| Senaryo | Sonuç |
|---|---|
| Sayfa açılışı, başlık, 11 seçim + 1 sayı alanı | ✅ |
| Marka seçilmeden model kapalı + "Önce marka seçin" | ✅ |
| Eksik alan → sarı uyarı | ✅ |
| Marka değişince model sıfırlanır | ✅ |
| Dolu form → **1.262.707 ₺** + aralık + kur | ✅ |
| Başka alana dokununca sonuç kalır | ✅ |
| Geçmiş açılır, satırlar görünür | ✅ |
| Model hakkında → MAE / R² görünür | ✅ |
| Telefon genişliği (390px) yükleniyor | ✅ |
| Console error | **0** |
| Sayfada "Traceback" | **yok** |

## 6. Sunucu logu

İlk taramada **gerçek bir hata bulundu**:

```
pyarrow.lib.ArrowInvalid: Could not convert '—' with type str:
tried to convert to int64, Conversion failed for column Silindir
```

**Sebep:** geçmiş tablosunda `cylinders=None` olan satıra `"—"` yazılınca `Silindir` sütunu karışık tip (int + str) oldu; Streamlit'in Arrow dönüşümü patladı. Kullanıcıya traceback gelmiyordu ama sunucu logunda hata birikiyordu.

**Düzeltme:** `history_rows()` yardımcı fonksiyonu eklendi; tüm hücreler `str`'e çevriliyor. Regresyon testi: `test_history_rows_tum_hucreler_metin`. Commit `44ab638`.

**Son kontrol:** sunucu logunda `Traceback / Error / Exception / ArrowInvalid` eşleşmesi **0**.

## 7. Kalan notlar / riskler

1. `get_options()` imzası `year` ve `mileage` anahtarlarıyla genişletildi — CONTRACT.md güncellemesi ve Kaan'ın onayı bekleniyor.
2. GitHub remote bağlı değil; commitler lokal. PR süreci bağlantıdan sonra başlayacak.
3. İlk 8 commit `meng-git`, son 12 commit `meng-IO` (yerel yazar ayarı sonradan yapıldı).
4. Ham veride 9.558 ilanın modeli ayrıştırılamamış; bunlar eğitimde "model yok" olarak kalıyor, arayüz seçeneklerine girmiyor.

## 8. Site durumu

- **Adres:** http://localhost:8501 · HTTP 200
- **Kaynak:** `/home/mertmengi/Desktop/arayuz-sifir-local`
- **Mod:** gerçek servis + SQLite + eğitilmiş model
- **Sunucu:** arka planda çalışıyor (PID değişebilir; `ss -ltnp | grep 8501` ile görülebilir)
