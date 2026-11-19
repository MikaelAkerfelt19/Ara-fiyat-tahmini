"""ARAYUZ_KONSEPT.md §5 — hata ve davranış durumlarının tamamı."""

import logging
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import src.core.mock_service as ms
from src.core.errors import ModelNotReadyError

APP = Path(__file__).resolve().parents[1] / "app.py"


def _app() -> AppTest:
    at = AppTest.from_file(APP).run()
    assert not list(at.exception), at.exception
    return at


def _dolu_form(at: AppTest) -> AppTest:
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series")
    at.selectbox[4].set_value("Dizel")
    at.selectbox[5].set_value("Otomatik")
    at.run()
    return at


def test_her_markanin_en_az_bir_modeli_var() -> None:
    """Marka listesi ile model listesi aynı eşiği kullanmalı (boş liste olmamalı)."""
    from src.core.api import service

    markalar = service.get_options()["brand"]
    assert markalar
    for marka in markalar:
        assert service.get_models_for_brand(marka), f"{marka} için model yok"


def test_ilk_acilis_durumu() -> None:
    at = _app()
    assert at.selectbox[1].disabled  # marka seçilmeden model kapalı
    assert "Önce marka seçin" in [c.value for c in at.caption]
    assert all(w.value == "Seçin" or w.value is not None for w in at.selectbox)
    assert not at.markdown  # sonuç alanı yok
    infolar = [i.value for i in at.info]
    assert "Henüz tahmin yapılmadı." in infolar
    assert "Model bilgisi henüz yok." in infolar


def test_eksik_alan_servis_cagrilmaz(monkeypatch: pytest.MonkeyPatch) -> None:
    cagri = []
    monkeypatch.setattr(ms, "predict", lambda car: cagri.append(car))
    at = _app()
    at.button[0].click().run()
    assert [w.value for w in at.warning] == ["Lütfen tüm alanları doldurun."]
    assert cagri == []
    assert not list(at.exception)


def test_model_hazir_degil(monkeypatch: pytest.MonkeyPatch) -> None:
    def hata(car):
        raise ModelNotReadyError()

    monkeypatch.setattr(ms, "predict", hata)
    at = _dolu_form(_app())
    at.button[0].click().run()
    assert [e.value for e in at.error] == [
        "Model henüz hazır değil. Lütfen daha sonra tekrar deneyin."
    ]
    assert not list(at.exception)


def test_gecersiz_girdi_mesaji_gosterilir(monkeypatch: pytest.MonkeyPatch) -> None:
    def hata(car):
        raise ValueError("Kilometre negatif olamaz.")

    monkeypatch.setattr(ms, "predict", hata)
    at = _dolu_form(_app())
    at.button[0].click().run()
    assert [e.value for e in at.error] == ["Kilometre negatif olamaz."]
    assert not list(at.exception)


def test_beklenmeyen_hata_traceback_vermez(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def hata(car):
        raise RuntimeError("beklenmeyen")

    monkeypatch.setattr(ms, "predict", hata)
    logging.disable(logging.CRITICAL)
    try:
        at = _dolu_form(_app())
        at.button[0].click().run()
    finally:
        logging.disable(logging.NOTSET)
    assert [e.value for e in at.error] == ["Bir sorun oluştu. Lütfen daha sonra tekrar deneyin."]
    assert not list(at.exception)
