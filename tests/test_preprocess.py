"""Temizlik ve başlık ayrıştırma testleri."""

import pandas as pd
import pytest

from src.ml.config import FEATURES, TARGET
from src.ml.preprocess import clean, filter_train_rows, parse_title


@pytest.mark.parametrize(
    "title, expected",
    [
        ("2019 Chery Tiggo 7", (2019, "Chery", "Tiggo")),
        ("2016 chevy impala LT", (2016, "Chevrolet", "Impala")),
        ("2019 Land Rover Range Rover SUPERCHARGED", (2019, "Land Rover", "Range Rover")),
        ("2015 Ford F-150 XLT", (2015, "Ford", "F150")),
        ("2016 Ford F150", (2016, "Ford", "F150")),
        ("2008 Toyota rav-4", (2008, "Toyota", "RAV4")),
        ("2026 Chevrolet Chevy Traverse LT", (2026, "Chevrolet", "Traverse")),
        ("Bmw. X5.  35 I.", (None, "BMW", "X5")),
        ("2014 Mercedes benz C250", (2014, "Mercedes-Benz", "C250")),
        ("Toyota Prius 2012 low miles", (2012, "Toyota", "Prius")),
        ("2021 Tesla Model 3", (2021, "Tesla", "Model 3")),
        ("2014 Mercedes-Benz C 250 C 250 2dr Coupe", (2014, "Mercedes-Benz", "C250")),
        ("2004 Infiniti G 35", (2004, "Infiniti", "G35")),
        ("2015 BMW 3 Series", (2015, "BMW", "3 Series")),
        ("100 John Deere 17ZTS Mini excavator", (None, None, None)),
        ("Electric Bike", (None, None, None)),
    ],
)
def test_parse_title(title, expected):
    assert parse_title(title) == expected


def _raw(**overrides) -> pd.DataFrame:
    base = {
        "ID": [1, 2, 3],
        "title": ["2019 Toyota Camry", "Electric Bike", "2015 Ford F-150"],
        "odometer": [100000, None, 5],
        "cylinders": ["6 cylinders", "other", None],
        "fuel": ["gas", "Diesel", "weird"],
        "transmission": ["automatic", "manual", None],
        "condition": ["good", None, "new"],
        "drive": ["fwd", "4wd", None],
        "type": ["sedan", "suv", None],
        "title_status": ["clean", "rebuilt", None],
        "price": [10000, 0, 20000],
    }
    base.update(overrides)
    return pd.DataFrame(base)


def test_clean_keeps_all_rows_and_converts_units():
    raw = _raw()
    out = clean(raw)
    assert len(out) == len(raw)
    assert out.loc[0, "mileage"] == 160934
    assert pd.isna(out.loc[1, "mileage"])
    assert out.loc[0, "cylinders"] == 6
    assert pd.isna(out.loc[1, "cylinders"])
    assert out.loc[0, "fuel_type"] == "Benzin"
    assert out.loc[1, "fuel_type"] == "Dizel"
    assert pd.isna(out.loc[2, "fuel_type"])
    assert out.loc[0, "drive"] == "Önden çekiş"
    assert pd.api.types.is_numeric_dtype(out["year"])


def test_filter_train_rows_drops_zero_price():
    out = filter_train_rows(clean(_raw()))
    assert (out[TARGET] > 0).all()
    assert set(FEATURES) <= set(out.columns)
