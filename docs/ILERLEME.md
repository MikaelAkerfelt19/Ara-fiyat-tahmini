# Faz ve commit öncesi inceleme kaydı

Bu kayıt `PLAN.md`, `GOREVLER_BACKEND.md` ve `CODEX_GOREV.md` sırasını izler.
Her yeni adımda kapsam ve bağımlılıklar kontrol edilir; bulgular burada yazılır,
gerekli düzeltmeler yapılır, bağımsız inceleme ve kabul komutlarından sonra commit atılır.
Test başarısı, insan ekip üyesinin PR onayından ayrı kaydedilir.

## Faz 0: Başlangıç — B0 ve B1

### Adım 1: Mevcut başlangıç kodunu doğrulama — 13 Ekim 2026

- Önceden tamamlanan kod: paket iskeleti, dokuz sabitlenmiş bağımlılık, dört sözleşme
  dosyası, yedi gerçek servis fonksiyonu taslağı, yalnızca başlık içeren uygulama,
  17 test, CI ve PR şablonu.
- Dal: `feature/core-iskelet`; başlangıç kodunun son commit'i: `9ee0e94`.
- Python 3.12.14 ortamında `ruff check .`: başarılı.
- `ruff format --check .`: 14 Python dosyası zaten biçimlendirilmiş.
- `pytest`: 17 test başarılı, 0.56 saniye.
- `pip check`: bozuk bağımlılık yok.
- Bu adım önceki kodu yeniden üretmez; kalan B0 işlerinin gerçek durumunu kaydeder.

**Bulgular ve çözüm:**

1. Plan hem her ara commit'te başarılı pytest istiyor hem testleri altıncı commit'te
   ekletiyor. Ayrıca üçüncü commit'in `api.py` dosyası, dördüncü commit'te oluşturulan
   gerçek servise bağlı. Önceki tarihsel commit'ler yeniden yazılmadı. Bundan sonraki
   her yeni commit tam ve çalışan test takımı üzerinden doğrulanacak.
2. Streamlit testi sandbox içinde Windows `asyncio` yerel soket kurulumu sırasında
   takılıyor. Aynı test takımı normal yerel izinlerle geçti; uygulama koduna ortama özel
   değişiklik yapılmadı.
3. Depoda görev issue'ları, proje etiketleri ve kilometre taşları henüz yok.
4. GitHub Projects için bağlı CLI kimliğinde `read:project` yetkisi yok. Pano kurulumu
   erişim sağlanana kadar bekleyecek; pano kurulumu tamamlandı sayılmayacak.

**İnceleme:** Bağımsız inceleme onaylandı; kritik veya önemli bulgu yok.
Önerilen ifade düzeltmeleri commit öncesinde uygulandı.

### Adım 2: Etiketler ve kilometre taşları — 13 Ekim 2026

- `ui`, `db`, `ml`, `core`, `docs` etiketleri oluşturuldu; mevcut `bug` etiketi korundu.
- [M1 — İskelet](https://github.com/MikaelAkerfelt19/Ara-fiyat-tahmini/milestone/1):
  18 Ekim 2026.
- [M2 — Gerçek model](https://github.com/MikaelAkerfelt19/Ara-fiyat-tahmini/milestone/2):
  1 Kasım 2026.
- [M3 — Teslim](https://github.com/MikaelAkerfelt19/Ara-fiyat-tahmini/milestone/3):
  6 Kasım 2026.
- Mevcut etiketler silinmedi; tekrar çalıştırmada aynı kayıtlar yeniden oluşturulmadı.
- GitHub API'den altı etiketin varlığı ve üç teslim tarihi yeniden okunup doğrulandı.

**Bulgu ve çözüm:** GitHub kilometre taşı `due_on` alanını takvim günü olarak,
`00:00:00Z` saatiyle saklıyor. İlk doğrulamanın saati birebir karşılaştırması yanlıştı.
Kontrol takvim tarihini karşılaştıracak şekilde düzeltildi; üç tarih planla eşleşiyor.
Uygulama kaynak kodunda hata veya değişiklik yok.

**İnceleme:** Bağımsız inceleme onaylandı; kritik veya önemli bulgu yok.
Plan tarihleri, etiketler, GitHub bağlantıları ve düzeltilen tarih kontrolü incelendi.

### Kalan başlangıç işleri

- [x] Proje etiketleri ve M1/M2/M3 kilometre taşları.
- [ ] B0–B11 ve A0–A10 görevlerini planın kabul ölçütleriyle issue olarak oluşturma.
- [ ] Başlangıç dalını PR ile incelemeye sunma ve GitHub CI sonucunu doğrulama.
- [ ] GitHub Projects panosu: Yapılacak → Yapılıyor → İncelemede → Bitti.
- [ ] Arkadaşı collaborator olarak ekleme: GitHub kullanıcı adı bekleniyor.
- [ ] B0 kabul ölçütü: arkadaşın depoyu klonlayıp bağımlılıkları hatasız kurması.
- [ ] Ekip incelemesi ve PR birleştirme: insan ekip üyesinin onayı bekleniyor.
- [ ] PR birleştikten sonra `main` için PR ve CI zorunluluğunu açma.

## Faz 1: Veri ve ilk arayüz — B2–B4, A1–A3

B2 sıradaki backend adımıdır. Gerçek `train.csv`, `test.csv` ve varsa
`sample_submission.csv` dosyaları henüz çalışma alanında yok; `DATA.md` şablondur.
Veri sütunları ve para birimi doğrulanmadan temizlik ya da model fazına geçilmez.

- [ ] B2: Veriyi tanıma ve DATA.md §1–4.
- [ ] Kontrol noktası 1: hedef, özellikler ve CarInput alanlarını kesinleştirme.
- [ ] B3: Bulgulara dayalı temizlik ve testleri.
- [ ] B4: EDA ve kontrol noktası 2.

Sonraki fazlar `PLAN.md` takvimindeki bağımlılıklara göre takip edilir. Gerçek veriyle
doğrulanmamış bir görev tamamlandı olarak işaretlenmez.
