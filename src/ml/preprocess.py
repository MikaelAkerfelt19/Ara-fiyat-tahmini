"""Ham ilan verisini temizler. clean() satır silmez; filter_train_rows() yalnızca eğitimde."""

import re

import pandas as pd

from src.ml.config import (
    BODY_LABELS,
    BRAND_ALIASES,
    CANONICAL_BRANDS,
    CONDITION_LABELS,
    DRIVE_LABELS,
    FEATURES,
    FUEL_LABELS,
    MILE_TO_KM,
    MIN_PRICE_USD,
    TARGET,
    TITLE_STATUS_LABELS,
    TRANSMISSION_LABELS,
)

_YEAR_RE = re.compile(r"(?<!\d)(19[3-9]\d|20[0-2]\d)(?!\d)")
_MIN_YEAR, _MAX_YEAR = 1930, 2027
_MAX_KM = 1_600_000
_FILLER_TOKENS = {"model", "series", "class", "range"}  # tek başına anlamsız model kelimeleri

# Marka arama tablosu: küçük harf ifade -> görünen ad
_BRAND_LOOKUP = {b.lower(): b for b in CANONICAL_BRANDS} | BRAND_ALIASES


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
        if len(tokens[i : i + 2]) == 2 and two in _BRAND_LOOKUP:
            brand, brand_end = _BRAND_LOOKUP[two], i + 2
            break
        if tokens[i] in _BRAND_LOOKUP:
            brand, brand_end = _BRAND_LOOKUP[tokens[i]], i + 1
            break
    if brand is None:
        return year, None, None

    # Yıl tokenını ve markanın tekrarını ("Chevrolet Chevy Traverse") atla
    rest = [
        t
        for t in tokens[brand_end:]
        if not (match and t == match.group(1)) and _BRAND_LOOKUP.get(t) != brand
    ]
    if not rest:
        return year, brand, None
    words = [rest[0]]
    if (rest[0] in _FILLER_TOKENS or len(rest[0]) == 1) and len(rest) > 1:
        words.append(rest[1])
    # Tireler kaldırılır; "F-150" ile "F150" aynı model sayılır
    return year, brand, " ".join(_format_word(w.replace("-", "")) for w in words)


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
    if TARGET in df.columns:
        out[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    return out


def filter_train_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Yalnızca eğitim: tekrarları, çok düşük fiyatları ve uç fiyatları çıkarır."""
    out = df.drop_duplicates(subset=FEATURES + [TARGET])
    out = out[out[TARGET] >= MIN_PRICE_USD]
    low, high = out[TARGET].quantile([0.005, 0.995])
    return out[(out[TARGET] >= low) & (out[TARGET] <= high)]
