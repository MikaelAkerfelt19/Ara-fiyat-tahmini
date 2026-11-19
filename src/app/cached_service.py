"""Sık değişmeyen servis verileri için önbellekli sarmalayıcılar.

Seçenekler, sınırlar ve model listeleri her etkileşimde yeniden okunmaz.
Değişen veriler (geçmiş, model bilgisi, tahmin) burada değildir; her turda taze okunur.
"""

import streamlit as st

from src.app.service_access import service


@st.cache_data(show_spinner=False)
def get_options() -> dict[str, list[str]]:
    return service.get_options()


@st.cache_data(show_spinner=False)
def get_ranges() -> dict[str, tuple[float, float]]:
    return service.get_ranges()


@st.cache_data(show_spinner=False)
def get_models_for_brand(brand: str) -> list[str]:
    return service.get_models_for_brand(brand)
