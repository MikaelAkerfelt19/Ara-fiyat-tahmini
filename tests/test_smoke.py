"""Başlangıç sayfasının sahte servis ortamında açıldığını doğrula."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_opens_without_errors():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value == "İkinci El Araç Fiyat Tahmini"
