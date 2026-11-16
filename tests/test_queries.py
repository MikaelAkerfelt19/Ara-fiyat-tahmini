"""Veritabanı sorguları; geçici veritabanı kullanır, data/ klasörü gerekmez."""

import sqlite3
from contextlib import closing

import pandas as pd
import pytest

from src.db import queries, schema


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "test.db")
    cars = pd.DataFrame(
        {
            "brand": ["Toyota", "Ford", "Toyota", "Toyota", None],
            "model": ["Camry", "Focus", "Corolla", "Camry", "X"],
            "year": [2010.0, 2015.0, 2020.0, None, 2000.0],
            "price": [5000, 7000, 9000, 6000, 1000],
        }
    )
    with closing(schema.connect()) as conn:
        schema.create_tables(conn)
        cars.to_sql("cars", conn, index=False)
        conn.commit()


def test_distinct_values_sorted_without_null(db):
    assert queries.distinct_values(["brand"]) == {"brand": ["Ford", "Toyota"]}


def test_models_for_brand_applies_min_listing_threshold(db, monkeypatch):
    # Eşik 1: tüm modeller listelenir (alfabetik)
    monkeypatch.setattr(queries, "MIN_MODEL_LISTINGS", 1)
    assert queries.models_for_brand("Toyota") == ["Camry", "Corolla"]
    assert queries.models_for_brand("Yok") == []
    # Eşik 2: yalnızca iki ilanı olan Camry kalır; tek ilanlı Corolla düşer
    monkeypatch.setattr(queries, "MIN_MODEL_LISTINGS", 2)
    assert queries.models_for_brand("Toyota") == ["Camry"]
    assert queries.models_for_brand("Ford") == []


def test_numeric_ranges_ignore_nan(db):
    low, high = queries.numeric_ranges(["year"])["year"]
    assert 2000 <= low < high <= 2020


def test_prediction_roundtrip_newest_first(db):
    queries.insert_prediction({"brand": "Ford"}, 100.6, "v1")
    queries.insert_prediction({"brand": "Toyota"}, 200.4, "v1")
    rows = queries.recent_predictions(5)
    assert [r["brand"] for r in rows] == ["Toyota", "Ford"]
    assert [r["price"] for r in rows] == [200, 101]


def test_insert_model_run_deactivates_previous(db):
    meta = {
        "trained_at": "2026-11-16T10:00:00",
        "model_name": "m",
        "version": "1",
        "n_train": 10,
        "mae": 1.0,
        "rmse": 2.0,
        "r2": 0.5,
    }
    queries.insert_model_run(meta, {"a": 1})
    queries.insert_model_run({**meta, "version": "2"}, {"a": 2})
    with closing(sqlite3.connect(schema.DB_PATH)) as conn:
        rows = conn.execute("SELECT version, is_active FROM model_runs ORDER BY id").fetchall()
    assert rows == [("1", 0), ("2", 1)]
