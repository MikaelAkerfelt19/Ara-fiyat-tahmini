"""Temizlik ve başlık ayrıştırma testleri."""

import pandas as pd
import pytest

from src.ml.config import FEATURES, TARGET
from src.ml.preprocess import clean, filter_report, filter_train_rows, parse_title


@pytest.mark.parametrize(
    "title, expected",
    [
        ("2019 Chery Tiggo 7", (2019, "Chery", "Tiggo")),
        ("2016 chevy impala LT", (2016, "Chevrolet", "Impala")),
        ("2019 Land Rover Range Rover SUPERCHARGED", (2019, "Land Rover", "Range Rover")),
        ("2018 Jeep Grand Cherokee Limited", (2018, "Jeep", "Grand Cherokee")),
        ("2015 Dodge Grand Caravan SXT", (2015, "Dodge", "Grand Caravan")),
        ("2012 Toyota Land Cruiser", (2012, "Toyota", "Land Cruiser")),
        ("2019 Hyundai Santa Fe SE", (2019, "Hyundai", "Santa Fe")),
        ("2016 Toyota RAV 4 XLE", (2016, "Toyota", "RAV 4")),
        ("2010 Chrysler Town & Country", (2010, "Chrysler", "Town Country")),
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


def test_clean_adds_title_column():
    assert list(clean(_raw())["title"]) == list(_raw()["title"])


def test_seller_type_from_vehicles_column():
    out = clean(_raw(seller_type=["dealer", "owner", None]))
    assert list(out["seller_type"]) == ["Galeri", "Bireysel", "Bireysel"]


def test_seller_type_from_text_when_no_column():
    out = clean(
        _raw(
            title=["2019 Toyota Camry", "2015 Ford F-150", "2014 Honda Civic"],
            features_list=["Call our dealer today", "Carfax available", "one owner, runs great"],
        )
    )
    assert list(out["seller_type"]) == ["Galeri", "Galeri", "Bireysel"]
    # title içindeki kalıp da sayılır; description sütunu da kabul edilir
    out = clean(
        _raw(
            title=["2019 Toyota Camry - financing available", "x", "y"],
            description=["", "no", "no"],
        )
    )
    assert out.loc[0, "seller_type"] == "Galeri"


def test_brand_falls_back_to_manufacturer():
    out = clean(
        _raw(
            title=["2015 XLT crew cab", "2012 Defender", "2015 Ford F-150"],
            manufacturer=["ford", "rover", "toyota"],
        )
    )
    assert out.loc[0, "brand"] == "Ford"
    assert out.loc[1, "brand"] == "Land Rover"
    assert out.loc[2, "brand"] == "Ford"  # başlıktaki marka yedekten önce gelir


def test_broken_odometer_nulls_mileage_but_keeps_row():
    raw = _raw(odometer=[100000, 50000, 70000], odometer_broken=[1, 0, 0])
    raw["odometer_rolled_over"] = [0, 1, 0]
    out = clean(raw)
    assert len(out) == 3
    assert out["mileage"].isna().tolist() == [True, True, False]


def _row(**kw) -> dict:
    base = {
        "brand": "Toyota",
        "model": "Camry",
        "year": 2015,
        "mileage": 100_000,
        "price": 10_000,
        "title_status": "Temiz",
    }
    return base | kw


def _frame(*rows: dict) -> pd.DataFrame:
    df = pd.DataFrame(list(rows))
    df["year"] = df["year"].astype("Int64")
    df["mileage"] = df["mileage"].astype("Int64")
    return df


@pytest.mark.parametrize(
    "bad",
    [
        _row(brand=None),
        _row(price=999),
        _row(price=250_001),
        _row(year=1949),
        _row(year=None),
        _row(mileage=None),
        _row(mileage=600_001),
        _row(mileage=1_500, year=2020),
        _row(title_status="Parça için"),
    ],
)
def test_filter_train_rows_drops_each_junk_rule(bad):
    good = _row(model="Corolla")
    out = filter_train_rows(_frame(good, bad))
    assert len(out) == 1 and out.iloc[0]["model"] == "Corolla"


def test_filter_train_rows_keeps_boundaries_and_new_cars():
    rows = [
        _row(price=1_000, model="A"),
        _row(price=250_000, model="B"),
        _row(year=1950, model="C"),
        _row(mileage=600_000, model="D"),
        _row(mileage=100, year=2025, model="E"),  # yeni araç: düşük km normal
    ]
    assert len(filter_train_rows(_frame(*rows))) == 5


def test_filter_train_rows_drops_duplicates():
    out = filter_train_rows(_frame(_row(), _row(), _row(price=10_001)))
    assert len(out) == 2


def test_filter_report_counts_each_rule_in_order():
    df = _frame(
        _row(),
        _row(),  # tekrar
        _row(brand=None),
        _row(price=500),
        _row(price=300_000),
        _row(year=1900),
        _row(mileage=None),
        _row(mileage=900_000),
        _row(mileage=500, year=2000),
        _row(title_status="Parça için"),
    )
    report = filter_report(df)
    counts = [n for _, n in report]
    # marka, düşük fiyat, yüksek fiyat, yıl, km yok/çok, sahte km, parça, tekrar
    assert counts == [1, 1, 1, 1, 2, 1, 1, 1]
    assert len(filter_train_rows(df)) == 1
    assert sum(counts) == len(df) - 1


def test_unify_model_names_picks_most_common_spelling_per_brand():
    from src.ml.preprocess import unify_model_names

    df = pd.DataFrame(
        {
            "brand": ["BMW", "BMW", "BMW", "Toyota", "Toyota", None],
            "model": ["3 Series", "3 Series", "3SERIES", "4RUNNER", "4 Runner", "X"],
        }
    )
    out = unify_model_names(df)
    assert len(out) == len(df)  # satır silmez
    assert out["model"].tolist()[:3] == ["3 Series"] * 3
    assert out.loc[3, "model"] == out.loc[4, "model"]
    assert out.loc[5, "model"] == "X"  # markasız satıra dokunulmaz
