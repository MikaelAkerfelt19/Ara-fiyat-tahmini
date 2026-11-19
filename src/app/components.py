"""Arayüz bölümlerini çizen yardımcı fonksiyonlar."""

import streamlit as st

from src.app.formatters import format_price, format_rate, format_score
from src.core.schemas import Prediction


def render_result(prediction: Prediction) -> None:
    """Tahmin sonucunu sayfanın en dikkat çekici öğesi olarak çizer."""
    st.caption("Tahmini fiyat")
    st.markdown(f"## {format_price(prediction.price)}")
    if prediction.low is not None and prediction.high is not None:
        low = format_price(prediction.low)
        high = format_price(prediction.high)
        st.caption(f"Olası aralık: {low} – {high}")
    if prediction.usd_try is not None:
        st.caption(f"Kullanılan kur: 1 USD = {format_rate(prediction.usd_try)} ₺")


_HISTORY_COLUMNS = {
    "created_at": "Tarih",
    "brand": "Marka",
    "model": "Model",
    "year": "Model yılı",
    "mileage": "Kilometre",
    "cylinders": "Silindir",
    "fuel_type": "Yakıt",
    "transmission": "Vites",
    "condition": "Durum",
    "drive": "Çekiş",
    "body_type": "Kasa tipi",
    "title_status": "Ruhsat durumu",
    "seller_type": "Satıcı tipi",
    "price": "Fiyat",
}


def history_rows(history: list[dict]) -> list[dict]:
    """Geçmiş satırlarını tabloya hazırlar.

    Tüm hücreler metindir: eksik değer "—" ile karışınca sayısal bir sütunda
    karışık tip oluşur ve Streamlit'in Arrow dönüşümü patlar (sunucu logunda
    ``ArrowInvalid`` görünür, kullanıcıya traceback gelmese de hata kaydı düşer).
    """
    rows = []
    for row in history:
        formatted = {}
        for key, label in _HISTORY_COLUMNS.items():
            value = row.get(key)
            formatted[label] = "—" if value is None else str(value)
        price = row.get("price")
        formatted["Fiyat"] = format_price(price) if price is not None else "—"
        rows.append(formatted)
    return rows


def render_history(history: list[dict]) -> None:
    """Son tahminleri varsayılan olarak kapalı bir açılır bölümde gösterir."""
    with st.expander("Son tahminler"):
        if not history:
            st.info("Henüz tahmin yapılmadı.")
            return
        st.dataframe(history_rows(history), hide_index=True)


def render_model_info(info: dict) -> None:
    """Model güvenilirliğini varsayılan olarak kapalı bir açılır bölümde gösterir."""
    with st.expander("Model hakkında"):
        if all(info.get(key) is None for key in ("mae", "rmse", "r2")):
            st.info("Model bilgisi henüz yok.")
            return

        symbol = "₺" if info.get("metrics_currency") == "TRY" else "$"
        st.caption(f"Model: {info.get('model_name', '—')} {info.get('version', '—')}")
        if info.get("trained_at"):
            st.caption(f"Eğitim tarihi: {str(info['trained_at'])[:10]}")

        col1, col2, col3 = st.columns(3)
        for column, key, label in (
            (col1, "mae", "MAE"),
            (col2, "rmse", "RMSE"),
            (col3, "r2", "R²"),
        ):
            value = info.get(key)
            if value is None:
                shown = "—"
            elif key == "r2":
                shown = format_score(value)
            else:
                shown = format_price(value, symbol)
            column.metric(label, shown)

        if info.get("n_train") is not None:
            count = f"{info['n_train']:,}".replace(",", ".")
            st.caption(f"Eğitim verisi: {count} ilan")
        if symbol == "$":
            st.caption("Hata ölçümleri USD cinsindendir (model dolar ile eğitildi).")
