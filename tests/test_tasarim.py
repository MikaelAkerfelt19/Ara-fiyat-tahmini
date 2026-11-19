"""ARAYUZ_KONSEPT.md §6 — tasarım ilkelerinin doğrulanması."""

import tomllib
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"


def test_tek_sayfa_html_css_yok() -> None:
    kod = APP.read_text(encoding="utf-8")
    assert "st.sidebar" not in kod  # kenar çubuğu yok
    assert "st.form(" not in kod  # form §8'de uygun değil
    for yasak in ("unsafe_allow_html", "components.v1", "<div", "<style"):
        assert yasak not in kod


def test_tek_vurgu_rengi_ve_sade_menu() -> None:
    assert APP.read_text(encoding="utf-8").count('type="primary"') == 1
    with (ROOT / ".streamlit/config.toml").open("rb") as dosya:
        config = tomllib.load(dosya)
    assert config["client"]["toolbarMode"] == "minimal"
    assert config["theme"]["primaryColor"].startswith("#")
    assert config["theme"]["font"] == "sans serif"


def test_metin_tutarliligi_ve_kapali_bolumler() -> None:
    at = AppTest.from_file(APP).run()
    assert not list(at.exception), at.exception
    kategori = {
        "Marka",
        "Model",
        "Yakıt",
        "Vites",
        "Durum",
        "Çekiş",
        "Kasa tipi",
        "Ruhsat durumu",
        "Satıcı tipi",
    }
    assert all(w.options[0] == "Seçin" for w in at.selectbox if w.label in kategori)
    assert [e.label for e in at.expander] == ["Son tahminler", "Model hakkında"]
    assert all(not e.proto.expanded for e in at.expander)


def test_sonuc_en_dikkat_cekimli_ogedir() -> None:
    at = AppTest.from_file(APP).run()
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series")
    at.selectbox[4].set_value("Dizel")
    at.selectbox[5].set_value("Otomatik")
    at.button[0].click().run()
    assert len(at.markdown) == 1
    assert at.markdown[0].value.startswith("## ")
