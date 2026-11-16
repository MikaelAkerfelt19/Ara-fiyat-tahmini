"""Ham ilan verisini temizler. clean() satır silmez; filter_train_rows() yalnızca eğitimde."""

import re

import numpy as np
import pandas as pd

from src.ml.config import (
    BODY_LABELS,
    BRAND_ALIASES,
    CANONICAL_BRANDS,
    CONDITION_LABELS,
    DEALER_PATTERN,
    DRIVE_LABELS,
    FUEL_LABELS,
    MAX_PRICE_USD,
    MILE_TO_KM,
    MIN_PRICE_USD,
    TARGET,
    TITLE_STATUS_LABELS,
    TRANSMISSION_LABELS,
)

_YEAR_RE = re.compile(r"(?<!\d)(19[3-9]\d|20[0-2]\d)(?!\d)")
_MIN_YEAR, _MAX_YEAR = 1930, 2027
_MAX_KM = 1_600_000
MAX_TRAIN_KM = 600_000  # eğitimde bundan fazla km şüpheli sayılır
_DUP_KEY = ["brand", "model", "year", "mileage", TARGET]  # aynı ilan tekrar girmiş mi
# Tek başına anlamsız model kelimeleri: bir sonraki kelimeyle birleşir. "Grand" tek başına
# Jeep Grand Cherokee, Dodge Grand Caravan ve Toyota Grand Highlander'ı aynı modele toplardı.
_FILLER_TOKENS = {
    "model", "series", "class", "range", "grand", "land", "santa", "town", "monte", "el",
    "new", "super", "rav",
}  # fmt: skip


def model_key(model: str) -> str:
    """Model adının yazımdan bağımsız anahtarı: "3 Series", "3SERIES" ve "3-series" -> "3SERIES"."""
    return re.sub(r"[^0-9A-Z]", "", str(model).upper())


def unify_model_names(df: pd.DataFrame) -> pd.DataFrame:
    """Aynı markada yazımı farklı ama aynı model olan adları en sık yazıma çevirir.

    Satır silmez. Tüm veri seti üzerinde çalışır (en sık yazımı bulmak için), bu yüzden
    clean() içinde değil, veritabanına yazmadan önce load_data'da çağrılır.
    """
    df = df.copy()
    known = df["model"].notna() & df["brand"].notna()
    keys = df.loc[known, "model"].map(model_key)
    sub = pd.DataFrame(
        {"brand": df.loc[known, "brand"], "key": keys, "model": df.loc[known, "model"]}
    )
    best = (
        sub.groupby(["brand", "key"])["model"]
        .agg(lambda s: s.value_counts().index[0])
        .rename("best")
    )
    joined = sub.join(best, on=["brand", "key"])
    df.loc[known, "model"] = joined["best"].to_numpy()
    return df


# Marka arama tablosu: küçük harf ifade -> görünen ad
_BRAND_LOOKUP = {b.lower(): b for b in CANONICAL_BRANDS} | BRAND_ALIASES
# Başlıkta "rover" tek başına marka sayılmaz: "Land Rover Range Rover" içindeki ikinci "Rover"
# model adının parçasıdır. "rover" takma adı yalnızca vehicles.csv manufacturer değeri içindir.
_TITLE_LOOKUP = {k: v for k, v in _BRAND_LOOKUP.items() if k != "rover"}


def _valid_year(value: int) -> int | None:
    """Yıl makul aralıktaysa döndürür."""
    return value if _MIN_YEAR <= value <= _MAX_YEAR else None


def _format_word(word: str) -> str:
    """Rakam içeren veya kısa kelimeler büyük harf, diğerleri baş harf büyük."""
    if any(ch.isdigit() for ch in word) or len(word) <= 3:
        return word.upper()
    return word.capitalize()


def parse_title(title: str) -> tuple[int | None, str | None, str | None]:
    """Başlıktan (yıl, marka, model) çıkarır; bulunamayan parça None olur."""
    if not isinstance(title, str):
        return None, None, None
    match = _YEAR_RE.search(title)
    year = _valid_year(int(match.group(1))) if match else None

    text = re.sub(r"[*,/!]", " ", title.lower())
    # Baştaki/sondaki nokta ve tireler atılır: "bmw." -> "bmw"
    tokens = [t.strip(".-") for t in text.split() if re.search(r"\w", t)]

    brand = None
    brand_end = 0
    for i in range(min(4, len(tokens))):
        two = " ".join(tokens[i : i + 2])
        if len(tokens[i : i + 2]) == 2 and two in _TITLE_LOOKUP:
            brand, brand_end = _TITLE_LOOKUP[two], i + 2
            break
        if tokens[i] in _TITLE_LOOKUP:
            brand, brand_end = _TITLE_LOOKUP[tokens[i]], i + 1
            break
    if brand is None:
        return year, None, None

    # Yıl tokenını ve markanın tekrarını ("Chevrolet Chevy Traverse") atla
    rest = [
        t
        for t in tokens[brand_end:]
        if not (match and t == match.group(1)) and _TITLE_LOOKUP.get(t) != brand
    ]
    if not rest:
        return year, brand, None
    words = [rest[0]]
    if (rest[0] in _FILLER_TOKENS or len(rest[0]) == 1) and len(rest) > 1:
        words.append(rest[1])
        # Tek HARF ("C 250", "G 35") bitişik yazılır: veride "C 250" ile "C250" aynı araç.
        # Rakamla başlayanlar ("3 Series") ve filler kelimeler ("Model 3") boşluklu kalır.
        if len(rest[0]) == 1 and rest[0].isalpha():
            return year, brand, _format_word((rest[0] + rest[1]).replace("-", ""))
    # Tireler kaldırılır; "F-150" ile "F150" aynı model sayılır. Birleşik adın ikinci kelimesi
    # rakam içermiyorsa baş harfi büyük yazılır ("Santa Fe", "Santa FE" değil).
    parts = [w.replace("-", "") for w in words]
    formatted = [_format_word(parts[0])] + [
        w.capitalize() if w.isalpha() else _format_word(w) for w in parts[1:]
    ]
    return year, brand, " ".join(formatted)


def _map_labels(series: pd.Series, labels: dict[str, str]) -> pd.Series:
    """Küçük harfe çevirip Türkçe etikete eşler; eşlemede olmayan NaN olur."""
    return series.astype("string").str.strip().str.lower().map(labels).astype(object)


def _year_from_raw(value) -> int | None:
    """Başlıkta yıl yoksa ham year sütununun baştaki 4 hanesi."""
    digits = str(value)[:4]
    return _valid_year(int(digits)) if digits.isdigit() else None


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Ham tabloyu model/veritabanı sütunlarına çevirir. Satır silmez."""
    parsed = df["title"].map(parse_title)
    out = pd.DataFrame(index=df.index)
    out["id"] = df["ID"]

    year = parsed.map(lambda t: t[0])
    if "year" in df.columns:
        year = year.where(year.notna(), df["year"].map(_year_from_raw))
    out["year"] = pd.to_numeric(year, errors="coerce").astype("Int64")

    km = (pd.to_numeric(df["odometer"], errors="coerce") * MILE_TO_KM).round()
    km = km.where((km > 0) & (km <= _MAX_KM))
    out["mileage"] = km.astype("Int64")

    cyl = df["cylinders"].astype("string").str.extract(r"(\d+)\s*cylinders?", expand=False)
    out["cylinders"] = pd.to_numeric(cyl, errors="coerce").astype("Int64")

    out["brand"] = parsed.map(lambda t: t[1]).astype(object)
    out["model"] = parsed.map(lambda t: t[2]).astype(object)
    out["fuel_type"] = _map_labels(df["fuel"], FUEL_LABELS)
    out["transmission"] = _map_labels(df["transmission"], TRANSMISSION_LABELS)
    out["condition"] = _map_labels(df["condition"], CONDITION_LABELS)
    out["drive"] = _map_labels(df["drive"], DRIVE_LABELS)
    out["body_type"] = _map_labels(df["type"], BODY_LABELS)
    out["title_status"] = _map_labels(df["title_status"], TITLE_STATUS_LABELS)

    # vehicles.csv'de ayrı bir üretici (manufacturer) sütunu var. Başlıktan marka çıkmayan
    # ilanlarda ("2015 F-150 XLT") bu sütun yedek olur; satır silinmez, yalnızca marka dolar.
    if "manufacturer" in df.columns:
        backup = df["manufacturer"].astype("string").str.strip().str.lower().map(_BRAND_LOOKUP)
        out["brand"] = out["brand"].where(out["brand"].notna(), backup.astype(object))

    out["seller_type"] = _seller_type(df)

    # Sayaç bozuk veya sıfırlanmışsa km değeri güvenilmezdir. Satırı silmeyiz (clean() silmez);
    # km'yi boş bırakırız, eğitimde "km yok" kuralı bu satırları eler.
    for flag in ("odometer_broken", "odometer_rolled_over"):
        if flag in df.columns:
            bad = pd.to_numeric(df[flag], errors="coerce").eq(1)
            out["mileage"] = out["mileage"].mask(bad)

    # title yalnızca sızıntı kontrolü içindir (iki set arasında aynı ilanı bulmak); veritabanına
    # ve modele girmez.
    out["title"] = df["title"]
    if TARGET in df.columns:
        out[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    return out


def _seller_type(df: pd.DataFrame) -> pd.Series:
    """Satıcı tipi: "Galeri" veya "Bireysel".

    vehicles.csv'de gerçek etiket var (dealer/owner), onu kullanırız. Kaggle verisinde etiket
    yok; ilan metninde galeri kalıpları (DEALER_PATTERN) aranır. Kalıp vehicles etiketine karşı
    sınandığında ilanların %86'sını doğru bildi.
    """
    if "seller_type" in df.columns:
        raw = df["seller_type"].astype("string").str.strip().str.lower()
        is_dealer = raw.eq("dealer").fillna(False).to_numpy(dtype=bool)
        return np.where(is_dealer, "Galeri", "Bireysel").astype(object)
    body_col = "features_list" if "features_list" in df.columns else "description"
    body = df[body_col] if body_col in df.columns else pd.Series("", index=df.index)
    text = body.fillna("").astype(str) + " " + df["title"].fillna("").astype(str)
    is_dealer = text.str.contains(DEALER_PATTERN, case=False, regex=True)
    return np.where(is_dealer, "Galeri", "Bireysel").astype(object)


def _junk_rules(df: pd.DataFrame) -> list[tuple[str, pd.Series]]:
    """(kural açıklaması, satırın kuralı geçip geçmediği) çiftleri. Sıra önemlidir:
    rapor her kuralın, öncekilerden sonra KALAN satırlardan kaç tanesini attığını gösterir."""
    year = df["year"].astype(float)
    km = df["mileage"].astype(float)
    return [
        # Markası olmayan ilan araç değildir (bisiklet, ekskavatör, reklam); modelin işi değil.
        ("marka bulunamayan (araç olmayan / reklam)", df["brand"].notna()),
        # Peşinat, "ara" ve tek haneli fiyatlar gerçek satış fiyatı değil.
        (f"fiyat {MIN_PRICE_USD:,} $ altı (peşinat / 'ara' ilanı)", df[TARGET] >= MIN_PRICE_USD),
        # Çok yüksek fiyat çoğunlukla fazladan yazılmış sıfırdır.
        (f"fiyat {MAX_PRICE_USD:,} $ üstü (hatalı)", df[TARGET] <= MAX_PRICE_USD),
        # Yıl yoksa ya da çok eskiyse aracın değeri koleksiyon mantığıyla işler.
        ("yıl 1950 öncesi veya yok", year >= 1950),
        # Km bilinmiyorsa (bozuk sayaç dahil) model en önemli ikinci özelliği göremez.
        (
            f"km yok, {MAX_TRAIN_KM:,} km üstü veya bozuk sayaç",
            km.between(0, MAX_TRAIN_KM),
        ),
        # Eski araç 2.000 km'den az gösteriyorsa sayaç sıfırlanmış / girilmemiştir.
        ("2.000 km altı ama 2024 öncesi (sahte km)", ~((km < 2_000) & (year < 2024))),
        # Parça için satılan araç, çalışan araç fiyatını bozar.
        ("'Parça için' ruhsat", df["title_status"].ne("Parça için")),
    ]


def filter_report(df: pd.DataFrame) -> list[tuple[str, int]]:
    """Her kuralın attığı satır sayısı (sırayla, öncekilerden kalan satırlar üzerinden).

    Son satır tekrar ilanlardır. Eğitime giren satır sayısı = len(df) - toplam.
    """
    keep = pd.Series(True, index=df.index)
    report = []
    for label, ok in _junk_rules(df):
        ok = ok.fillna(False).astype(bool)
        report.append((label, int((keep & ~ok).sum())))
        keep &= ok
    kept = df[keep]
    report.append(
        ("tekrar ilan (marka, model, yıl, km, fiyat aynı)", int(kept.duplicated(_DUP_KEY).sum()))
    )
    return report


def filter_train_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Yalnızca eğitim: çöp ilanları ve tekrarları çıkarır (kurallar _junk_rules'ta).

    Eski %0,5 / %99,5 yüzdelik kesimi kaldırıldı: yüzdelik, verinin ne kadar kirli olduğuna
    göre değişir ve iyi ilanları da keser. Sabit, açıklanabilir kurallar sunumda anlatılabilir.
    """
    keep = pd.Series(True, index=df.index)
    for _label, ok in _junk_rules(df):
        keep &= ok.fillna(False).astype(bool)
    return df[keep].drop_duplicates(subset=_DUP_KEY)
