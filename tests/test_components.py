"""Arayüz bölümlerinin (components) testleri."""

from streamlit.testing.v1 import AppTest

from src.app.components import history_rows

_ONUZ = """
from src.app.components import render_result
from src.core.schemas import Prediction
render_result(Prediction(price=18450, low=16605, high=20300, model_version="test", usd_try=40.0))
"""

_GECBOS = """
from src.app.components import render_history
render_history([])
"""

_GEC_DOLU = """
from src.app.components import render_history
render_history([{
    "created_at": "2026-11-18T10:00:00", "brand": "BMW", "model": "320i",
    "year": 2020, "mileage": 50000, "cylinders": 4, "fuel_type": "Dizel",
    "transmission": "Otomatik", "condition": None, "drive": None,
    "body_type": None, "title_status": None, "seller_type": None,
    "price": 880000,
}])
"""

_MODEL_YOK = """
from src.app.components import render_model_info
render_model_info({"model_name": None, "version": None, "mae": None, "rmse": None,
                   "r2": None, "n_train": None, "metrics_currency": None})
"""

_MODEL_VAR = """
from src.app.components import render_model_info
render_model_info({"model_name": "HistGB", "version": "v2", "trained_at": "2026-11-16",
                   "mae": 4315, "rmse": 5800, "r2": 0.799, "n_train": 168365,
                   "metrics_currency": "USD"})
"""


def _calistir(kod: str) -> AppTest:
    at = AppTest.from_string(kod).run()
    assert not list(at.exception), at.exception
    return at


def test_render_result_fiyat_ve_aralik() -> None:
    at = _calistir(_ONUZ)
    assert [m.value for m in at.markdown] == ["## 18.450 ₺"]
    captions = [c.value for c in at.caption]
    assert "Olası aralık: 16.605 ₺ – 20.300 ₺" in captions
    assert not any("Kullanılan kur" in c for c in captions)


def test_render_history_bos() -> None:
    at = _calistir(_GECBOS)
    assert [i.value for i in at.info] == ["Henüz tahmin yapılmadı."]


def test_history_rows_tum_hucreler_metin() -> None:
    """Eksik değerler '—' olunca sütun karışık tipe düşmesin (ArrowInvalid)."""
    satirlar = history_rows(
        [
            {
                "created_at": "2026-11-19T10:00:00",
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2015,
                "mileage": 100_000,
                "cylinders": None,
                "fuel_type": "Benzin",
                "transmission": "Otomatik",
                "condition": None,
                "drive": None,
                "body_type": None,
                "title_status": None,
                "seller_type": None,
                "price": 1_262_707,
            }
        ]
    )
    satir = satirlar[0]
    assert all(isinstance(v, str) for v in satir.values())
    assert satir["Silindir"] == "—"
    assert satir["Fiyat"] == "1.262.707 ₺"


def test_render_history_satir() -> None:
    at = _calistir(_GEC_DOLU)
    row = at.dataframe[0].value.iloc[0]
    assert row["Fiyat"] == "880.000 ₺"
    assert row["Durum"] == "—"
    assert row["Model yılı"] == "2020"


def test_render_model_info_yok() -> None:
    at = _calistir(_MODEL_YOK)
    assert [i.value for i in at.info] == ["Model bilgisi henüz yok."]


def test_render_model_info_var() -> None:
    at = _calistir(_MODEL_VAR)
    assert [m.value for m in at.metric] == ["4.315 $", "5.800 $", "0,799"]
    captions = [c.value for c in at.caption]
    assert "Eğitim verisi: 168.365 ilan" in captions
    assert any("Hata ölçümleri USD cinsindendir" in c for c in captions)
