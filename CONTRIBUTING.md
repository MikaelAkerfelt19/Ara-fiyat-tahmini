# Katkı Kuralları

İki kişi aynı repoda çalışıyoruz. Bu kurallar birbirimizin kodunu bozmamamız ve commit geçmişinin düzenli görünmesi için var. Hoca katkı geçmişine bakabilir, o yüzden ikimizin de düzenli commit atması önemli.

## 1. İlk kurulum (bir kez)

```bash
git config --global user.name "Ad Soyad"
git config --global user.email "github-hesabindaki@eposta.com"
```

Commit'lerin GitHub profilinde görünmesi için e-posta, GitHub hesabındakiyle aynı olmalı.

## 2. Dallar

- `main`: **her zaman çalışan sürüm.** Buraya doğrudan push yapılmaz, her şey Pull Request (PR) ile gelir.
- İş dalları her zaman güncel `main`'den açılır:

| Tür | Biçim | Örnek |
|---|---|---|
| Yeni özellik | `feature/<alan>-<kisa-ad>` | `feature/ui-tahmin-formu`, `feature/ml-baseline` |
| Hata düzeltme | `fix/<kisa-ad>` | `fix/kilometre-dogrulama` |
| Belge | `docs/<kisa-ad>` | `docs/data-sozlugu` |

`<alan>` şunlardan biri olur: `ui`, `db`, `ml`, `core`.

Mümkünse GitHub'da **Settings → Branches** altından `main` için "Require a pull request before merging" kuralını açın. Özel repolarda bu ayar GitHub Pro gerektirebilir; GitHub Student Developer Pack ile ücretsiz alınabilir. Açamazsanız kuralı kendiniz uygulayın.

## 3. Günlük döngü

```bash
git switch main
git pull
git switch -c feature/ml-baseline

# ... çalış, küçük adımlarla commit at ...
git add <dosyalar>
git commit -m "feat(ml): medyan baseline ve MAE ölçümü ekle"

git push -u origin feature/ml-baseline
# GitHub'da PR aç → diğer kişi inceler → birleştirilir
```

İş uzun sürdüyse ve `main` ilerlediyse, PR açmadan önce dalını güncelle:

```bash
git switch main && git pull
git switch feature/ml-baseline
git merge main
```

## 4. Commit mesajları

Biçim: `tür(alan): kısa açıklama`. Açıklama Türkçe, emir kipinde ve en fazla 72 karakter olmalı.

| Tür | Ne zaman |
|---|---|
| `feat` | Yeni özellik |
| `fix` | Hata düzeltme |
| `docs` | Sadece belge |
| `refactor` | Davranışı değiştirmeyen düzenleme |
| `test` | Test ekleme veya düzeltme |
| `chore` | Bağımlılık, ayar, `.gitignore` vb. |

Örnekler:

```
feat(ui): marka seçilince model listesini güncelle
feat(db): cars ve predictions tablolarını oluştur
fix(ml): test verisinde satır silinmesini engelle
docs: DATA.md veri sözlüğünü doldur
chore: requirements sürümlerini sabitle
```

**Küçük ve sık commit at.** Her anlamlı adım bir commit olsun ve günde en az bir kez push et. "Bir hafta çalışıp tek dev commit" yapmayın.

## 5. Pull Request kuralları

- PR başlığı commit biçiminde olur: `feat(ui): tahmin formu`.
- Açıklamada şunlar bulunur:
  - **Ne değişti?** (1–3 madde)
  - **Nasıl test ettim?** (komut veya adımlar)
  - Arayüz değişikliklerinde **ekran görüntüsü**
  - İlgili issue: `Closes #12`
- **İnceleyen kişi her zaman diğer ekip üyesidir.** 24 saat içinde incelenir.
- Birleştirme yöntemi: **"Create a merge commit"**. Squash kullanmıyoruz ki tek tek commit'ler geçmişte görünsün.
- `src/core/` altındaki **sözleşme dosyalarına** dokunan bir PR iki kişinin onayı olmadan birleştirilmez (bkz. `docs/CONTRACT.md`).

## 6. Issue'lar ve proje panosu

- `docs/GOREVLER_*.md` içindeki her görev bir GitHub Issue'dur. Issue başlığı görev koduyla başlar: `B6 — Baseline model`, `A3 — Bağımlı marka/model seçimi`.
- **Projects** sekmesinde bir pano açılır. Kolonlar: `Yapılacak` → `Yapılıyor` → `İncelemede` → `Bitti`.
- Etiketler: `ui`, `db`, `ml`, `core`, `docs`, `bug`.
- Milestone'lar: `M1 — İskelet (18 Ekim)`, `M2 — Gerçek model (1 Kasım)`, `M3 — Teslim (6 Kasım)`.

## 7. Repoya asla girmeyecekler

`.gitignore` bunları zaten dışarıda tutar, yine de dikkat edin:

- `data/` (Kaggle verisi ve `cars.db`). Yarışma verisi yeniden paylaşılamaz.
- `models/*.joblib` (final model GitHub **Releases**'e eklenir)
- `kaggle.json` ve her türlü anahtar/şifre
- `.venv/`, `__pycache__/`

Notebook'larda grafik çıktıları kalabilir, ama binlerce satırlık tablo çıktısı bırakmayın.

## 8. Kod stili

- Kaydetmeden veya commit atmadan önce `ruff format .` ve `ruff check .` çalıştırın.
- Kodda isimler (değişken, fonksiyon) **İngilizce**, yorumlar ve arayüz metinleri **Türkçe** olur.
- `src/core/` altındaki fonksiyonlarda tip ipuçları (type hints) zorunludur.
