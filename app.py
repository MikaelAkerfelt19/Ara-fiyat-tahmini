"""İkinci el araç fiyat tahmini — arayüz giriş noktası."""

import logging

import streamlit as st

from src.app.cached_service import (
    get_models_for_brand,
    get_options,
    get_ranges,
    get_years_for_model,
)
from src.app.components import render_history, render_model_info, render_result
from src.app.formatters import format_km
from src.app.service_access import service
from src.core.errors import ModelNotReadyError
from src.core.schemas import CarInput

logger = logging.getLogger(__name__)

EMPTY_CHOICE = "Seçin"
NO_CYLINDER_FUELS = {"Elektrik", "Hibrit"}


def optional_choice(value: str) -> str | None:
    """Boş seçimi servise None olarak gönderir."""
    return None if value == EMPTY_CHOICE else value


st.set_page_config(page_title="İkinci El Araç Fiyat Tahmini", layout="centered")

st.title("İkinci El Araç Fiyat Tahmini")
st.caption("Aracın bilgilerini gir, tahmini piyasa fiyatını gör.")

# Kullanıcı onayıyla yapılan tek HTML/CSS istisnası: hareketli arka plan.
st.markdown(
    """
    <style>
    @keyframes zeminHareketi {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }
    [data-testid="stAppViewContainer"] {
      background: linear-gradient(
        120deg, #DCEBFF 0%, #B9D6FF 25%, #F4F7FB 50%, #C9DFFF 75%, #DCEBFF 100%
      );
      background-size: 300% 300%;
      animation: zeminHareketi 7s linear infinite;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if service is None:
    st.error(
        "Gerçek servis henüz bağlanmadı. Şimdilik USE_MOCK=1 ile çalıştırın "
        "(USE_MOCK=1 streamlit run app.py)."
    )
    st.stop()

options = get_options()
ranges = get_ranges()
mileage_options = options["mileage"]

# Alanlar gizliyken servise boş değer gönderilmez.
year = None
mileage = None
fuel_type = transmission = EMPTY_CHOICE
condition = drive = body_type = title_status = seller_type = EMPTY_CHOICE
cylinders = None

# Adım 1 — marka
brand = st.selectbox("Marka", [EMPTY_CHOICE, *options["brand"]], key="brand", filter_mode="fuzzy")

if brand != st.session_state.get("_last_brand", brand):
    st.session_state["model"] = EMPTY_CHOICE
st.session_state["_last_brand"] = brand

# Adım 2 — model
if brand != EMPTY_CHOICE:
    model = st.selectbox(
        "Model",
        [EMPTY_CHOICE, *get_models_for_brand(brand)],
        key="model",
        filter_mode="fuzzy",
    )
else:
    model = EMPTY_CHOICE
    st.caption("Önce marka seçin")

# Adım 3 — model yılı (marka+model için veride var olan yıllar, yeniden eskiye)
if model != EMPTY_CHOICE:
    if model != st.session_state.get("_last_model", model):
        for key in (
            "year",
            "mileage",
            "fuel_type",
            "transmission",
            "condition",
            "drive",
            "body_type",
            "title_status",
            "seller_type",
        ):
            st.session_state[key] = EMPTY_CHOICE
    st.session_state["_last_model"] = model

    years = get_years_for_model(brand, model)
    if years:
        year = st.selectbox(
            "Model yılı", years, index=None, placeholder="Seçin", key="year", filter_mode="fuzzy"
        )

        # Adım 4 — kilometre
        if year is not None:
            mileage = st.selectbox(
                "Kilometre",
                mileage_options,
                index=None,
                placeholder="Seçin",
                format_func=format_km,
                key="mileage",
                filter_mode="fuzzy",
            )

            # Adım 5 — yakıt
            if mileage is not None:
                fuel_type = st.selectbox(
                    "Yakıt", [EMPTY_CHOICE, *options["fuel_type"]], key="fuel_type"
                )

                # Adım 6 — vites
                if fuel_type != EMPTY_CHOICE:
                    transmission = st.selectbox(
                        "Vites",
                        [EMPTY_CHOICE, *options["transmission"]],
                        key="transmission",
                    )

                    # Adım 7 — isteğe bağlı alanlar
                    if transmission != EMPTY_CHOICE:
                        if fuel_type not in (EMPTY_CHOICE, *NO_CYLINDER_FUELS):
                            cylinders_min, cylinders_max = (int(v) for v in ranges["cylinders"])
                            cylinders = st.number_input(
                                "Silindir",
                                min_value=cylinders_min,
                                max_value=cylinders_max,
                                value=cylinders_min,
                                key="cylinders",
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            condition = st.selectbox(
                                "Durum",
                                [EMPTY_CHOICE, *options["condition"]],
                                key="condition",
                            )
                        with col2:
                            drive = st.selectbox(
                                "Çekiş", [EMPTY_CHOICE, *options["drive"]], key="drive"
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            body_type = st.selectbox(
                                "Kasa tipi",
                                [EMPTY_CHOICE, *options["body_type"]],
                                key="body_type",
                            )
                        with col2:
                            title_status = st.selectbox(
                                "Ruhsat durumu",
                                [EMPTY_CHOICE, *options["title_status"]],
                                key="title_status",
                            )

                        seller_type = st.selectbox(
                            "Satıcı tipi",
                            [EMPTY_CHOICE, *options["seller_type"]],
                            key="seller_type",
                        )
    else:
        st.info("Bu araç için model yılı verisi bulunamadı.")

if st.button("Fiyatı Tahmin Et", type="primary"):
    choices = (brand, model, year, mileage, fuel_type, transmission)
    if not all(choices) or any(c == EMPTY_CHOICE for c in choices):
        st.warning("Lütfen tüm alanları doldurun.")
    else:
        car = CarInput(
            brand=brand,
            model=model,
            year=year,
            mileage=mileage,
            fuel_type=fuel_type,
            transmission=transmission,
            condition=optional_choice(condition),
            cylinders=cylinders,
            drive=optional_choice(drive),
            body_type=optional_choice(body_type),
            title_status=optional_choice(title_status),
            seller_type=optional_choice(seller_type),
        )
        try:
            with st.spinner("Hesaplanıyor…"):
                prediction = service.predict(car)
        except ModelNotReadyError:
            st.error("Model henüz hazır değil. Lütfen daha sonra tekrar deneyin.")
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            logger.exception("Beklenmeyen tahmin hatası")
            st.error("Bir sorun oluştu. Lütfen daha sonra tekrar deneyin.")
        else:
            service.save_prediction(car, prediction)
            st.session_state["last_prediction"] = prediction

if "last_prediction" in st.session_state:
    render_result(st.session_state["last_prediction"])

# Geçmiş ve model bilgisi her turda servisten taze okunur (önbelleğe alınmaz)
render_history(service.get_history(limit=10))
render_model_info(service.get_model_info())
