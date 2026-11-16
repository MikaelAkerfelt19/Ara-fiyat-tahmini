"""USD/TRY kuru: TCMB günlük kur dosyasından çekilir, internet yoksa yedek kur kullanılır."""

import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date

TCMB_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
# TCMB 16.11.2026 döviz satış 50,3942; internet yoksa kullanılır.
FALLBACK_USD_TRY = 50.39
FALLBACK_SOURCE = "yedek kur"
# TLS el sıkışması bu makinede 3 sn'yi aşabiliyor; günde bir kez ödenen bedel olduğu için 10 sn.
TIMEOUT_SECONDS = 10


def parse_tcmb_xml(xml_text: str) -> float:
    """TCMB XML'inden USD döviz satış kurunu okur."""
    root = ET.fromstring(xml_text)
    node = root.find("Currency[@CurrencyCode='USD']/ForexSelling")
    if node is None or not node.text:
        raise ValueError("TCMB verisinde USD kuru bulunamadı.")
    return float(node.text)


def _fetch() -> tuple[float, str]:
    """TCMB'den kuru çeker; hata olursa istisna fırlatır."""
    with urllib.request.urlopen(TCMB_URL, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310
        xml_text = response.read().decode("utf-8")
    rate = parse_tcmb_xml(xml_text)
    published = ET.fromstring(xml_text).get("Tarih", date.today().isoformat())
    return rate, f"TCMB {published}"


# Önbellek: başarılı kur gün boyunca saklanır (kur günde bir güncellenir, her tahminde ağa
# gitmek yavaş olurdu). Hata olursa yedek kur yalnızca RETRY_SECONDS boyunca kullanılır;
# sonra TCMB yeniden denenir. Böylece tek bir ağ hatası bütün günü yedek kura bağlamaz,
# internet yokken de her tahmin TIMEOUT_SECONDS beklemez.
RETRY_SECONDS = 600
_cache: dict = {"day": None, "value": None, "failed_at": None}


def _clear_cache() -> None:
    _cache.update(day=None, value=None, failed_at=None)


def get_usd_try() -> tuple[float, str]:
    """(kur, kaynak) döndürür."""
    today = date.today().isoformat()
    if _cache["day"] == today:
        return _cache["value"]
    failed_at = _cache["failed_at"]
    if failed_at is not None and time.monotonic() - failed_at < RETRY_SECONDS:
        return FALLBACK_USD_TRY, FALLBACK_SOURCE
    try:
        value = _fetch()
    except Exception:  # noqa: BLE001
        # Ağ, XML veya okuma hatası ne olursa olsun servis çökmemeli.
        _cache["failed_at"] = time.monotonic()
        return FALLBACK_USD_TRY, FALLBACK_SOURCE
    _cache.update(day=today, value=value, failed_at=None)
    return value
