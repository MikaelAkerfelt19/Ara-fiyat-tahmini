"""Fiyat ve kur biçimlendirme yardımcıları."""

CURRENCY = "₺"  # README: fiyatlar TL cinsindendir


def format_price(price: float, currency: str = CURRENCY) -> str:
    """Fiyatı Türkçe biçimde, binlik ayırıcı nokta ve kuruşsuz döndürür.

    Örnek: ``format_price(18450) -> "18.450 ₺"``
    """
    return f"{round(price):,}".replace(",", ".") + f" {currency}"


def format_rate(rate: float) -> str:
    """Kuru Türkçe biçimde, iki kuruşlu ve virgüllü döndürür.

    Örnek: ``format_rate(40.0) -> "40,00"``
    """
    return f"{rate:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_km(km: int) -> str:
    """Kilometreyi Türkçe binlik ayırıcıyla döndürür (örn. ``150.000``)."""
    return f"{km:,}".replace(",", ".")


def format_score(value: float, digits: int = 3) -> str:
    """R² gibi ölçümleri Türkçe ondalık ayırıcıyla döndürür.

    Örnek: ``format_score(0.799) -> "0,799"``
    """
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")
