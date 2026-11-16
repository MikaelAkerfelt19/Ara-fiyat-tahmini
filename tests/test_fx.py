"""TCMB kur okuma testleri (ağa çıkmaz)."""

import pytest

from src.core import fx

XML = """<?xml version="1.0"?>
<Tarih_Date Tarih="16.11.2026" Date="11/16/2026">
  <Currency CurrencyCode="EUR"><ForexSelling>58.1000</ForexSelling></Currency>
  <Currency CurrencyCode="USD"><ForexSelling>50.3942</ForexSelling></Currency>
</Tarih_Date>"""


def test_parse_tcmb_xml_reads_usd_selling():
    assert fx.parse_tcmb_xml(XML) == pytest.approx(50.3942)


def test_get_usd_try_falls_back_when_network_fails(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("ağ yok")

    fx._clear_cache()
    monkeypatch.setattr(fx.urllib.request, "urlopen", boom)
    try:
        assert fx.get_usd_try() == (fx.FALLBACK_USD_TRY, "yedek kur")
    finally:
        fx._clear_cache()


def test_failure_is_not_cached_for_the_whole_day(monkeypatch):
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise OSError("geçici hata")
        return 50.0, "TCMB test"

    fx._clear_cache()
    monkeypatch.setattr(fx, "_fetch", flaky)
    try:
        assert fx.get_usd_try() == (fx.FALLBACK_USD_TRY, "yedek kur")
        # Bekleme süresi dolmadan yeniden denenmez (internet yokken her tahmin beklemesin)
        assert fx.get_usd_try() == (fx.FALLBACK_USD_TRY, "yedek kur")
        assert calls["n"] == 1
        # Bekleme süresi dolunca TCMB yeniden denenir ve başarılı kur gün boyu saklanır
        monkeypatch.setattr(fx, "RETRY_SECONDS", 0)
        assert fx.get_usd_try() == (50.0, "TCMB test")
        assert fx.get_usd_try() == (50.0, "TCMB test")
        assert calls["n"] == 2
    finally:
        fx._clear_cache()
