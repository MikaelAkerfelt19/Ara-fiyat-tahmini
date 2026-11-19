"""AppTest ile arayüz davranış testleri (sahte servis)."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"

TUM_ALANLAR = [
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


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not list(at.exception), at.exception
    return at


def _marka_model_yil_km(at: AppTest) -> AppTest:
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series").run()
    at.selectbox[2].set_value(at.selectbox[2].options[0]).run()
    at.selectbox[3].set_value(50_000).run()
    return at


def _doldur(at: AppTest) -> AppTest:
    at = _marka_model_yil_km(at)
    at.selectbox[4].set_value("Dizel").run()
    at.selectbox[5].set_value("Otomatik").run()
    return at


def _sonuc(at: AppTest) -> list:
    """CSS enjeksiyonu hariç gerçek sonuç başlıklarını döndürür."""
    return [m for m in at.markdown if m.value.startswith("## ")]


def test_asamali_acilis_ve_yil_sirasi() -> None:
    at = _app()
    assert [w.label for w in at.selectbox] == ["Marka"]
    assert not at.number_input

    at.selectbox[0].set_value("BMW").run()
    assert [w.label for w in at.selectbox] == ["Marka", "Model"]

    at.selectbox[1].set_value("3 Series").run()
    assert [w.label for w in at.selectbox] == ["Marka", "Model", "Model yılı"]
    yillar = at.selectbox[2].options
    assert yillar == sorted(yillar, reverse=True)  # en yeniden eskiye

    at.selectbox[2].set_value(yillar[0]).run()
    assert [w.label for w in at.selectbox] == [
        "Marka",
        "Model",
        "Model yılı",
        "Kilometre",
    ]

    at.selectbox[3].set_value(50_000).run()
    assert [w.label for w in at.selectbox][:5] == [
        "Marka",
        "Model",
        "Model yılı",
        "Kilometre",
        "Yakıt",
    ]

    at.selectbox[4].set_value("Dizel").run()
    assert [w.label for w in at.selectbox][:6] == TUM_ALANLAR[:6]
    assert not at.number_input  # vites seçilmeden silindir gizli

    at.selectbox[5].set_value("Otomatik").run()
    assert [w.label for w in at.selectbox] == TUM_ALANLAR
    assert [w.label for w in at.number_input] == ["Silindir"]
    assert [e.label for e in at.expander] == ["Son tahminler", "Model hakkında"]
    assert not _sonuc(at)  # ilk açılışta sonuç yok


def test_bos_formda_uyari_verir() -> None:
    at = _app()
    at.button[0].click().run()
    assert [w.value for w in at.warning] == ["Lütfen tüm alanları doldurun."]
    assert not _sonuc(at)


def test_tam_formda_sonuc_gorunur() -> None:
    at = _doldur(_app())
    at.button[0].click().run()
    assert len(_sonuc(at)) == 1
    assert "₺" in _sonuc(at)[0].value
    captions = [c.value for c in at.caption]
    assert any(c.startswith("Olası aralık:") for c in captions)
    assert not any("Kullanılan kur" in c for c in captions)
    assert not list(at.exception)


def test_sonuc_baska_alana_dokununca_kalir() -> None:
    at = _doldur(_app())
    at.button[0].click().run()
    sonuc = _sonuc(at)[0].value
    at.selectbox[0].set_value("Ford").run()
    assert [m.value for m in _sonuc(at)] == [sonuc]


def test_marka_degisince_model_sifirlanir() -> None:
    at = _app()
    assert "Önce marka seçin" in [c.value for c in at.caption]

    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series").run()
    at.selectbox[2].set_value(at.selectbox[2].options[0]).run()
    at.selectbox[0].set_value("Ford").run()
    assert at.selectbox[1].value == "Seçin"
    assert "F150" in at.selectbox[1].options
    assert [w.label for w in at.selectbox] == ["Marka", "Model"]


def test_model_secilmeden_diger_alanlar_gizli() -> None:
    at = _app()
    at.selectbox[0].set_value("Toyota").run()
    assert [w.label for w in at.selectbox] == ["Marka", "Model"]
    assert not at.number_input


def test_son_tahminler_en_yeni_ustte() -> None:
    at = _doldur(_app())
    at.button[0].click().run()
    at.selectbox[3].set_value(10_000)
    at.button[0].click().run()
    rows = at.dataframe[0].value
    assert len(rows) == 2
    assert rows.iloc[0]["Kilometre"] == "10000"
    assert rows.iloc[0]["Fiyat"] != rows.iloc[1]["Fiyat"]


def test_yil_secilmeden_uyari_verir() -> None:
    at = _app()
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series").run()
    at.button[0].click().run()
    assert [w.value for w in at.warning] == ["Lütfen tüm alanları doldurun."]
    assert not list(at.exception)


def test_kilometre_secilmeden_uyari_verir() -> None:
    at = _app()
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series").run()
    at.selectbox[2].set_value(at.selectbox[2].options[0]).run()
    at.button[0].click().run()
    assert [w.value for w in at.warning] == ["Lütfen tüm alanları doldurun."]
    assert not list(at.exception)


def test_yakitsiz_ve_vitessiz_uyari_verir() -> None:
    at = _app()
    at.selectbox[0].set_value("BMW").run()
    at.selectbox[1].set_value("3 Series").run()
    at.selectbox[2].set_value(at.selectbox[2].options[0]).run()
    at.selectbox[3].set_value(50_000).run()
    at.button[0].click().run()
    assert [w.value for w in at.warning] == ["Lütfen tüm alanları doldurun."]
    assert not list(at.exception)
