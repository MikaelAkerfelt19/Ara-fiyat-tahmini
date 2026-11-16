"""Segment ve katsayı önceliği testleri."""

import pytest

from src.ml.localization import factor_for, segment_of

LOC = {
    "default": 1.0,
    "segments": {"suv": 2.0, "ekonomik": 3.0},
    "overrides": {"Toyota|RAV4": 5.0},
}


@pytest.mark.parametrize(
    "row, expected",
    [
        ({"brand": "Tesla", "model": "Model 3", "fuel_type": "Elektrik"}, "elektrik"),
        ({"brand": "BMW", "model": "X5", "fuel_type": "Benzin", "body_type": "SUV"}, "premium"),
        ({"brand": "Toyota", "model": "RAV4", "fuel_type": "Benzin", "body_type": "SUV"}, "suv"),
        (
            {"brand": "Honda", "model": "Civic", "fuel_type": "Benzin", "body_type": "Sedan"},
            "ekonomik",
        ),
    ],
)
def test_segment_of(row, expected):
    assert segment_of(row) == expected


def test_factor_priority_override_segment_default():
    assert factor_for({"brand": "Toyota", "model": "RAV4", "body_type": "SUV"}, LOC) == 5.0
    assert factor_for({"brand": "Kia", "model": "X", "body_type": "SUV"}, LOC) == 2.0
    assert factor_for({"brand": "BMW", "model": "X5", "body_type": "SUV"}, LOC) == 1.0
