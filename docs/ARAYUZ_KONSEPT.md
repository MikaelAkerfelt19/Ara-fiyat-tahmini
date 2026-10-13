# Arayüz Konsept Belgesi

> Kimin için: Arayüzü (frontend) geliştirecek ekip üyesi · Hazırlayan: Kaan · Teslim: 9 Kasım 2026

Bu belge arayüzde **ne** yapılacağını anlatır, **nasıl** yapılacağını değil. Kod örneği yok. Hangi bileşeni nasıl kuracağına, kodu nasıl düzenleyeceğine sen karar vereceksin. Burada yalnızca hedef, sınırlar ve "bitti" sayılma ölçütleri var.

Bir şey belirsiz kalırsa tahmin yürütme, sor. Belgedeki kurallardan biri işine engel oluyorsa da söyle, birlikte değiştiririz.

---

## 1. Proje bir bakışta

- **Ne yapıyoruz?** Bir aracın özelliklerinden (marka, model, yıl, kilometre…) ikinci el piyasa fiyatını tahmin eden bir web uygulaması.
- **Veri:** Kaggle'daki *Used Car Price Prediction Challenge* yarışmasının verisi.
- **Neden?** Python dersi dönem projesi. **Her şey Python ile yazılacak.** Bu, dersin şartı.
- **Kim ne yapıyor?**
  - **Kaan:** veri, veritabanı, model eğitimi ve arayüzün çağıracağı servis katmanı
  - **Sen:** kullanıcının gördüğü web arayüzü
- **Arayüz teknolojisi:** **Streamlit.** Python'la web arayüzü yazmaya yarayan bir kütüphane. HTML, CSS veya JavaScript yazılmaz.

---

## 2. Sistem nasıl çalışıyor, sen neredesin?

```
 Kullanıcı (tarayıcı)
        │
        ▼
 ┌──────────────────┐
 │  ARAYÜZ  (sen)   │   app.py — Streamlit
 └────────┬─────────┘
          │  yalnızca "service" fonksiyonları
          ▼
 ┌──────────────────┐
 │  SERVİS (Kaan)   │   src/core/
 └────────┬─────────┘
          │
    ┌─────┴──────┐
    ▼            ▼
 Veritabanı    Model
 (SQLite)      (scikit-learn)
```

**Temel kural:** Arayüz veritabanına da model dosyasına da doğrudan dokunmaz. Neye ihtiyacın varsa (seçenek listeleri, tahmin, geçmiş) **servis** fonksiyonlarından istersin. Servisin içinde ne olduğunu bilmen gerekmiyor.

**Sahte servis (mock):** Kaan'ın modeli ilk haftalarda hazır olmayacak. Bu sürede sahte bir servisle çalışırsın. Fonksiyonlar gerçeğiyle aynı, sadece uydurma sonuçlar döndürüyor. Model hazır olunca tek bir ortam değişkeniyle gerçeğine geçilir; senin kodunda hiçbir şey değişmez. Bu sayede ikimiz de birbirimizi beklemeden çalışırız.

---

## 3. Kullanıcı ve senaryo

**Kullanıcı:** Arabasını satmayı ya da ikinci el araba almayı düşünen, teknik bilgisi olmayan biri. "Bu araç aşağı yukarı kaç eder?" sorusuna hızlıca cevap arıyor.

**Ana akış:**
1. Sayfayı açar. Başlığı ve tek satırlık açıklamayı görür.
2. Markayı seçer. O markanın modelleri listelenir, birini seçer.
3. Model yılını, kilometreyi, yakıt türünü ve vitesi girer.
4. "Fiyatı Tahmin Et" butonuna basar.
5. Tahmini fiyatı büyük, okunaklı bir şekilde ve altında olası fiyat aralığını görür.
6. İsterse daha önce yapılmış tahminlere ya da modelin ne kadar başarılı olduğuna bakar.

Tüm akış **tek sayfada** ve 30 saniyeden kısa sürede bitebilmeli.

---

## 4. Ekran

Tek sayfa. Yukarıdan aşağıya şu bölümler var:

```
┌────────────────────────────────────────────┐
│  İkinci El Araç Fiyat Tahmini              │  ← Başlık
│  Aracın bilgilerini gir, tahmini piyasa    │  ← Açıklama
│  fiyatını gör.                             │
│                                            │
│  Marka       [Seçin    ▼]  Model    [▼]    │
│  Model yılı  [2020   - +]  Kilometre [   ] │  ← Form
│  Yakıt       [Seçin    ▼]  Vites    [▼]    │
│                                            │
│  [ Fiyatı Tahmin Et ]                      │  ← Ana buton
│                                            │
│  Tahmini fiyat                             │
│  18.450 $                                  │  ← Sonuç
│  Olası aralık: 16.900 $ – 20.100 $         │
│                                            │
│  ▸ Son tahminler                           │  ← Kapalı açılır bölüm
│  ▸ Model hakkında                          │  ← Kapalı açılır bölüm
└────────────────────────────────────────────┘
```

| Bölüm | Amacı | İçeriği |
|---|---|---|
| Başlık ve açıklama | Kullanıcı sayfanın ne işe yaradığını anında anlasın | Bir başlık, bir satır açıklama |
| Form | Araç bilgisini toplamak | İki sütun. Seçenekli alanlar açılır liste, sayılar sınırlı sayı kutusu |
| Ana buton | Tahmini başlatmak | Sayfadaki tek renkli (vurgulu) öğe |
| Sonuç | Cevabı vermek | Büyük fiyat, altında küçük yazıyla olası aralık |
| Son tahminler | Önceki tahminlere bakmak | En yenisi üstte, en fazla 10 satırlık tablo |
| Model hakkında | Modelin güvenilirliğini göstermek | Ortalama hata, R², eğitim verisi sayısı, model adı ve sürümü |

**Form alanları (geçici):** marka, model, model yılı, kilometre, yakıt türü, vites. Kaan veri setini inceledikten sonra (1. hafta sonu) kesin alan listesini `CONTRACT.md`'de güncelleyip sana haber verecek. Birkaç alan eklenebilir veya çıkabilir, ama sayfanın yapısı aynı kalır. O zamana kadar bu altı alanla çalış.

---

## 5. Davranış kuralları

Arayüz her durumda ne yapacağını bilmeli. Uygulama hiçbir durumda kullanıcıya kırmızı bir Python hata ekranı (traceback) göstermemeli.

| Durum | Kullanıcı ne görür? |
|---|---|
| Sayfa ilk açıldığında | Seçenekli alanlar boş ("Seçin"). Sayı alanlarında makul varsayılan değerler. Sonuç alanı yok |
| Marka seçilmeden | Model listesi kapalı, "Önce marka seçin" yazıyor |
| Marka seçilince | Model listesinde yalnızca o markanın modelleri var |
| Marka değiştirilince | Önceki model seçimi temizlenir. Eski markanın modeli seçili kalmamalı |
| Sayı alanları | Alt ve üst sınırları servisten gelir. Kullanıcı sınır dışı değer giremez |
| Eksik alanla butona basılınca | Sarı uyarı: "Lütfen tüm alanları doldurun." Servis hiç çağrılmaz |
| Tahmin hesaplanırken | Kısa bir "Hesaplanıyor…" göstergesi |
| Tahmin başarılı olunca | Sonuç bölümü görünür. Tahmin, geçmişe kaydedilir |
| Kullanıcı tahminden sonra başka bir alana dokununca | Son sonuç ekranda **kalır**, kaybolmaz |
| Model henüz hazır değilse | Anlaşılır bir hata: "Model henüz hazır değil…" |
| Servis girdiyi geçersiz bulursa | Servisin verdiği mesaj, kırmızı hata kutusunda gösterilir |
| Henüz hiç tahmin yapılmamışsa | "Son tahminler" bölümünde "Henüz tahmin yapılmadı." |
| Model bilgisi yoksa (sahte serviste böyle) | "Model hakkında" bölümünde "Model bilgisi henüz yok." |

**Sayı biçimi:** Fiyatlar Türkçe biçimde, binlik ayırıcı nokta ve kuruşsuz yazılır: `18.450 $`. Para birimi veri setine göre belli olacak; Kaan bildirecek. Bu biçimlendirmeyi tek bir yardımcı fonksiyonda topla ve onun için test yaz.

---

## 6. Tasarım ilkeleri

Hedef: **sade, şık, dikkat dağıtmayan** bir sayfa.

- Tek sayfa, ortalanmış dar düzen. Kenar çubuğu (sidebar) yok.
- **Tek vurgu rengi**, o da yalnızca ana butonda.
- Emoji, ikon, süs görseli yok.
- Sayfadaki en dikkat çekici öğe **sonuç** olmalı.
- İkincil bilgiler (geçmiş, model bilgisi) varsayılan olarak kapalı açılır bölümlerde durur.
- Metinler Türkçe, kısa ve tutarlı. "Seçin" mi "Seçiniz" mi, birini seç ve her yerde onu kullan.
- Hata mesajı kullanıcıya ne yapması gerektiğini söylemeli.
- Tarayıcı telefon genişliğine daraltılınca da düzgün okunmalı.
- Görünüm yalnızca Streamlit'in tema ayar dosyasıyla (`.streamlit/config.toml`) ayarlanır. **Sayfaya HTML veya CSS gömülmez**; projenin Python şartıyla çelişir.
- Streamlit'in sağ üstteki geliştirici menüsü sade (minimal) moda alınmalı.

---

## 7. Backend ile sözleşme

Kesin imzalar ve sahte servisin kodu **`CONTRACT.md`** içinde. Burada fikri özetliyorum.

**Servise erişim:** Arayüz, servisi tek bir yerden alır: `src.core.api` modülündeki `service` nesnesi. Bu nesne ortam değişkenine göre sahte ya da gerçek servisi verir. Hangisinin geldiğini arayüzün bilmesine gerek yok.

**Servisin sana verdikleri:**

| Fonksiyon | Ne verir | Nerede kullanırsın |
|---|---|---|
| `get_options()` | Her seçenekli alan için seçenek listesi (marka, yakıt, vites…) | Açılır listeler |
| `get_models_for_brand(marka)` | O markanın modelleri | Model listesi |
| `get_ranges()` | Sayısal alanların alt ve üst sınırları | Sayı kutularının sınırları |
| `predict(araç)` | Tahmini fiyat, olası aralığın alt ve üst sınırı, model sürümü | Buton |
| `save_prediction(araç, tahmin)` | Tahmini geçmişe kaydeder | Başarılı tahminden hemen sonra |
| `get_history(adet)` | Son tahminlerin listesi | "Son tahminler" |
| `get_model_info()` | Model adı, sürüm, eğitim tarihi, hata ölçüleri, eğitim verisi sayısı | "Model hakkında" |

**Veri paketleri:** Formdan topladığın bilgiyi `CarInput` adlı veri sınıfına koyup `predict`'e verirsin. `predict` sana `Prediction` adlı bir sonuç döndürür. İkisi de `src/core/schemas.py` içinde.

**Olası hatalar:** `predict` iki tür hata fırlatabilir: model hazır değilse `ModelNotReadyError`, girdi geçersizse `ValueError`. İkisini de yakalayıp kullanıcıya düzgün bir mesaj göstermelisin (§5).

**Kurallar:**
- Seçenekleri ve sınırları **koda sabit yazma**, her zaman servisten al. Gerçek veriye geçildiğinde form kendiliğinden güncellenmeli.
- `src/core/` klasöründeki dosyaları **tek başına değiştirme.** Bir şeye ihtiyacın olursa Kaan'a söyle; sözleşme iki kişinin onayıyla değişir.
- Sık değişmeyen veriler (seçenekler, sınırlar, model listeleri) önbelleğe alınmalı. Her etkileşimde veritabanına gidilmemeli. Her tahminde değişen veriler (geçmiş, model bilgisi) ise önbelleğe alınmamalı.

**Sahte servisle çalıştırma:**
- macOS / Linux: `USE_MOCK=1 streamlit run app.py`
- Windows PowerShell: `$env:USE_MOCK="1"; streamlit run app.py`

---

## 8. Streamlit'te bilmen gereken kavramlar

Kodu sen yazacaksın. Ama şu kavramları anlamadan başlarsan kafan karışır. Her birini Streamlit belgelerinde (https://docs.streamlit.io) ara ve küçük bir denemeyle kendin gör.

1. **Betik her etkileşimde baştan çalışır.** Kullanıcı bir kutuya dokunduğunda `app.py` en baştan, yukarıdan aşağıya yeniden çalışır. Bütün davranışı buna göre düşün.
2. **Widget'lar değer döndürür ve bir kimliği (`key`) vardır.** Streamlit bir widget'ı kimliğine göre hatırlar. Kimlik değişirse widget sıfırlanır. "Marka değişince model sıfırlansın" kuralını bununla çözebilirsin.
3. **Buton yalnızca basıldığı turda "basılı" sayılır.** Bir sonraki etkileşimde sonuç kaybolur. Sonucun ekranda kalması için **session state** kavramına bak.
4. **Önbellek (`cache_data`)**, aynı çağrının sonucunu saklayıp tekrar hesaplamamaya yarar.
5. **`st.form` bu projede uygun değil.** Form içindeki alanlar değiştiğinde sayfa yeniden çalışmaz; bu yüzden markaya bağlı model listesi güncellenmez. Nedenini anlamak için bir kez dene.
6. **`AppTest`**, Streamlit'in kendi test aracıdır. Sayfayı tarayıcı açmadan çalıştırıp alan doldurabilir ve butona basabilir. Testlerini bununla yazacaksın.
7. **Tema ayarları** (`.streamlit/config.toml`): vurgu rengi, yazı tipi, açık tema, araç çubuğu modu.

---

## 9. Yapılacaklar

Her görev GitHub'da bir issue olarak açılacak. Issue başlığı görev koduyla başlar: `A3 — Bağımlı marka/model seçimi`. Bir görevi "bitti" saymak için sağdaki ölçütün sağlanması gerekir.

### Hafta 1 (12–18 Ekim): İskelet → **M1**

| Kod | Görev | Bitti sayılır, eğer… |
|---|---|---|
| A0 | Ortam kurulumu | Repo klonlandı, sanal ortam kuruldu, bağımlılıklar yüklendi, sahte servisle `streamlit run app.py` boş sayfayı açıyor |
| A1 | Sayfa iskeleti ve tema | Başlık ve açıklama görünüyor, tek vurgu rengi tanımlı, geliştirici menüsü sade. Fiyat biçimlendirme yardımcısı yazıldı ve testi geçiyor |
| A2 | Tahmin formu | Bütün alanlar var, seçenekler ve sınırlar servisten geliyor, butona basınca (sahte) bir fiyat görünüyor |
| A3 | Bağımlı marka → model seçimi | Marka seçilmeden model kapalı; marka değişince model listesi değişiyor ve önceki seçim temizleniyor |

**M1 (18 Ekim):** Sahte servisle uçtan uca çalışan form `main` dalında.

### Hafta 2 (19–25 Ekim): Davranış ve bölümler

| Kod | Görev | Bitti sayılır, eğer… |
|---|---|---|
| A4 | Doğrulama ve hata mesajları | §5'teki eksik alan, model hazır değil ve geçersiz girdi durumlarının hepsi denendi; hiçbirinde uygulama çökmüyor |
| A5 | Sonuç bölümü | Fiyat ve olası aralık görünüyor; sonrasında başka bir alana dokununca sonuç kaybolmuyor |
| A6 | Son tahminler | Üç tahmin yapılınca üçü de en yenisi üstte olacak şekilde listeleniyor; boşken bilgi mesajı var |
| A7 | Model hakkında | Model bilgisi varsa ölçüler, yoksa bilgi mesajı görünüyor |

### Hafta 3 (26 Ekim – 1 Kasım): Gerçek modele geçiş → **M2**

| Kod | Görev | Bitti sayılır, eğer… |
|---|---|---|
| A8 | Önbellek ve cila | Sabit veriler önbellekte, değişenler değil. Telefon genişliğinde düzgün. Metinler tutarlı. §6'daki ilkelerin hepsi sağlanıyor |
| A9 | Gerçek servise geçiş | Kaan "servis hazır" deyince sahte mod kapatılarak uygulama gerçek veriyle çalışıyor. Uzun marka ve model listelerinde arama yapılabiliyor. Üç gerçekçi araçla makul fiyatlar alındı. Para birimi doğru |

**M2 (1 Kasım):** Gerçek modelle çalışan uygulama.

### Hafta 4 (2–8 Kasım): Teslim → **M3**

| Kod | Görev | Bitti sayılır, eğer… |
|---|---|---|
| A10 | Testler, ekran görüntüleri, README | En az üç arayüz testi var ve geçiyor: sayfa hatasız açılır, boş formda uyarı çıkar, tam doldurulmuş formda sonuç görünür. Testler sahte servisle çalışıyor. Boş form, sonuçlu form ve açık "Son tahminler" ekran görüntüleri `docs/img/` altında. README'deki ekran görüntüsü bölümü dolu. Sunumdaki arayüz slaytları hazır |

**M3 (6 Kasım):** Teslime hazır sürüm (`v1.0`). 7–8 Kasım tampon günleri.

---

## 10. Senin dosyaların

| Dosya / klasör | Sahibi | Not |
|---|---|---|
| `app.py` | Sen | Arayüzün giriş noktası |
| `.streamlit/config.toml` | Sen | Tema |
| `src/app/` | Sen | Arayüz yardımcıları (fiyat biçimi vb.) |
| `tests/test_app.py`, `tests/test_components.py` | Sen | Arayüz testleri |
| `docs/img/` | Sen | Ekran görüntüleri |
| `src/core/` | **Ortak** | Sözleşme. Tek başına değiştirilmez |
| `src/db/`, `src/ml/`, `notebooks/` | Kaan | Dokunmana gerek yok |

**Senin kararın olanlar:** Vurgu renginin tonu, metinlerin ifadesi, alanların küçük düzen detayları, kodu dosyalara nasıl böleceğin. Kapsamı aşmayan küçük iyileştirmeler de serbest (örneğin formu temizleme butonu); eklemeden önce haber ver yeter.

**Senin kararın olmayanlar:** Teknoloji (Streamlit, sadece Python), tek sayfa yapısı, form alanları ve sözleşme.

---

## 11. Çalışma şekli

Ayrıntılar **`CONTRIBUTING.md`** içinde. Özetle:

- **`main` dalına doğrudan push yok.** Her iş ayrı bir dalda yapılır: `feature/ui-tahmin-formu` gibi.
- **Commit mesajı biçimi:** `feat(ui): markaya bağlı model listesi`. Küçük ve sık commit at, günde en az bir kez push et. Hoca commit geçmişine bakabilir.
- İş bitince **Pull Request** aç: ne değişti, nasıl test ettin, arayüz değişikliği varsa ekran görüntüsü ve `Closes #<issue>`.
- **Kaan PR'ını 24 saat içinde inceler**, yorum yazar, sonra birleştirilir.
- Veri dosyaları, `.venv` klasörü, model dosyaları ve şifreler **asla** commit'lenmez.

**Haftalık ritim:**
- **Pazartesi:** Haftanın issue'larını panoda "Yapılıyor"a çek.
- **Perşembe:** Entegrasyon günü. Açık PR'lar birleştirilir, `main` iki bilgisayarda da çalıştırılır.
- **Pazar:** Kısa demo. Takıldığın yerleri burada birlikte çözeriz.

**Takıldığında** issue'ya veya Kaan'a şunları yaz: ne yapmaya çalıştığını, hata mesajının tamamını ve bir ekran görüntüsü. "Çalışmıyor" tek başına yeterli değil.

---

## 12. Teslimden önce son kontrol

- [ ] Sahte servis kapalıyken uygulama gerçek veriyle açılıyor ve tahmin veriyor
- [ ] §5'teki her durum denendi, hiçbirinde traceback görünmüyor
- [ ] §6'daki tasarım ilkelerinin hepsi sağlanıyor
- [ ] Kodda sabit yazılmış seçenek veya sınır yok
- [ ] `pytest` geçiyor, `ruff check .` temiz
- [ ] Ekran görüntüleri ve README güncel
- [ ] Commit geçmişinde senin adınla düzenli commit'ler var
- [ ] Canlı demo provası yapıldı

---

## 13. Sık sorulanlar

**Form alanları değişirse ne olacak?**
Kaan `CONTRACT.md`'yi ve sahte servisi güncelleyip haber verir. Sen de formu yeni alanlara göre düzenlersin. Seçenekleri servisten aldığın sürece değişiklik küçük olur.

**Gerçek servise geçince kodumda ne değişecek?**
Hiçbir şey. Sadece uygulamayı sahte mod olmadan çalıştırırsın. Bir şey değiştirmen gerekiyorsa sözleşmeye uyulmayan bir yer var demektir; birlikte bakarız.

**Gerçek fiyatlar saçma çıkarsa?**
Bu senin değil, modelin sorunu. Ekran görüntüsüyle Kaan'a bildir.

**Kodu yapay zekâya yazdırabilir miyim?**
Takıldığın bir yer için yardım almak sorun değil. Ama sunumda hoca herhangi bir satırı "bu ne yapıyor?" diye sorabilir. Yazdığın her satırı açıklayabiliyor olmalısın.

---

**Ekteki belgeler:**
- `CONTRACT.md`: servis fonksiyonlarının kesin imzaları ve sahte servis
- `CONTRIBUTING.md`: git kuralları, dal ve commit biçimi, PR süreci
