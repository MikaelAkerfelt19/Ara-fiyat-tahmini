import pytest

from src.app.formatters import format_price, format_rate


@pytest.mark.parametrize(
    ("price", "expected"),
    [
        (18450, "18.450 ₺"),
        (1500.6, "1.501 ₺"),  # kuruşsuz, en yakın tam sayıya yuvarlanır
        (0, "0 ₺"),
        (1_234_567.89, "1.234.568 ₺"),
    ],
)
def test_format_price(price: float, expected: str) -> None:
    assert format_price(price) == expected


def test_format_price_para_birimi_degistirilebilir() -> None:
    assert format_price(18450, "USD") == "18.450 USD"


@pytest.mark.parametrize(
    ("rate", "expected"),
    [(40.0, "40,00"), (39.87, "39,87"), (1_234.5, "1.234,50")],
)
def test_format_rate(rate: float, expected: str) -> None:
    assert format_rate(rate) == expected
