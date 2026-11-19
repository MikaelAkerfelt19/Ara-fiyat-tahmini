"""AppTest ile arayüz davranış testleri (sahte servis)."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def _app() -> AppTest:
    at = AppTest.from_file(APP).run()
    assert not list(at.exception), at.exception
    return at


def _doldur(at: AppTest) -> AppTest:
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series")
    at.selectbox[2].set_value(2020)
    at.selectbox[3].set_value(50_000)
    at.selectbox[4].set_value("Dizel")
    at.selectbox[5].set_value("Otomatik")
    at.run()
    return at


def test_sayfa_hatasiz_acilir() -> None:
    at = _app()
    assert [w.label for w in at.selectbox] == [
        "Marka",
        "Model",
        "Model yılı",
        "Kilometre",
        "Yakıt",
        "Vites",
        "Durum",
        "Çekiş",
        "Kasa tipi",
        "Ruhsat durumu",
        "Satıcı tipi",
    ]
    assert [w.label for w in at.number_input] == ["Silindir"]
    assert [e.label for e in at.expander] == ["Son tahminler", "Model hakkında"]
    assert not at.markdown  # ilk açılışta sonuç yok


def test_bos_formda_uyari_verir() -> None:
    at = _app()
    at.button[0].click().run()
    assert [w.value for w in at.warning] == ["Lütfen tüm alanları doldurun."]
    assert not at.markdown


def test_tam_formda_sonuc_gorunur() -> None:
    at = _doldur(_app())
    at.button[0].click().run()
    assert [m.value for m in at.markdown] == ["## 880.000 ₺"]
    captions = [c.value for c in at.caption]
    assert "Olası aralık: 792.000 ₺ – 968.000 ₺" in captions
    assert "Kullanılan kur: 1 USD = 40,00 ₺" in captions
    assert not list(at.exception)


def test_sonuc_baska_alana_dokununca_kalir() -> None:
    at = _doldur(_app())
    at.button[0].click().run()
    at.selectbox[0].set_value("Ford").run()
    assert [m.value for m in at.markdown] == ["## 880.000 ₺"]


def test_marka_degisince_model_sifirlanir() -> None:
    at = _app()
    assert at.selectbox[1].disabled
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series").run()
    at.selectbox[0].set_value("Ford").run()
    assert at.selectbox[1].value == "Seçin"
    assert at.selectbox[1].options == [
        "Seçin",
        "Bronco",
        "Edge",
        "Escape",
        "Expedition",
        "Explorer",
        "F-150",
        "Focus",
        "Fusion",
        "Mustang",
        "Ranger",
        "Taurus",
        "Transit",
    ]


def test_son_tahminler_en_yeni_ustte() -> None:
    at = _doldur(_app())
    at.button[0].click().run()
    at.selectbox[3].set_value(10_000)
    at.button[0].click().run()
    rows = at.dataframe[0].value
    assert len(rows) == 2
    assert rows.iloc[0]["Kilometre"] == "10000"
    assert rows.iloc[0]["Fiyat"] != rows.iloc[1]["Fiyat"]
