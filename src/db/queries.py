"""Veritabanı sorguları. Servis katmanı ve train.py bunları kullanır."""

import json
from contextlib import closing
from datetime import datetime

import pandas as pd

from src.db.schema import connect


def load_cars() -> pd.DataFrame:
    with closing(connect()) as conn:
        return pd.read_sql("SELECT * FROM cars", conn)


def distinct_values(columns: list[str]) -> dict[str, list[str]]:
    # Sütun adları yalnızca config.py'den gelir, kullanıcıdan değil.
    out = {}
    with closing(connect()) as conn:
        for col in columns:
            rows = conn.execute(
                f'SELECT DISTINCT "{col}" FROM cars WHERE "{col}" IS NOT NULL ORDER BY 1'
            ).fetchall()
            out[col] = [r[0] for r in rows]
    return out


def models_for_brand(brand: str) -> list[str]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT DISTINCT model FROM cars WHERE brand = ? AND model IS NOT NULL ORDER BY 1",
            (brand,),
        ).fetchall()
    return [r[0] for r in rows]


def numeric_ranges(columns: list[str]) -> dict[str, tuple[float, float]]:
    # Sütun adları yalnızca config.py'den gelir. NaN/NULL değerler yüzdeliklere katılmaz.
    cols = ", ".join(f'"{c}"' for c in columns)
    with closing(connect()) as conn:
        df = pd.read_sql(f"SELECT {cols} FROM cars", conn)
    return {
        c: (float(df[c].dropna().quantile(0.01)), float(df[c].dropna().quantile(0.99)))
        for c in columns
    }


def insert_prediction(inputs: dict, price: float, model_version: str) -> None:
    with closing(connect()) as conn:
        conn.execute(
            "INSERT INTO predictions (created_at, input_json, predicted_price, model_version) "
            "VALUES (?, ?, ?, ?)",
            (
                datetime.now().isoformat(timespec="seconds"),
                json.dumps(inputs, ensure_ascii=False),
                price,
                model_version,
            ),
        )
        conn.commit()


def recent_predictions(limit: int = 20) -> list[dict]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT created_at, input_json, predicted_price FROM predictions "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {"created_at": created, **json.loads(inputs), "price": round(price)}
        for created, inputs, price in rows
    ]


def insert_model_run(meta: dict, params: dict) -> None:
    with closing(connect()) as conn:
        conn.execute("UPDATE model_runs SET is_active = 0")
        conn.execute(
            "INSERT INTO model_runs (created_at, model_name, version, params_json, n_train, "
            "mae, rmse, r2, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (
                meta["trained_at"],
                meta["model_name"],
                meta["version"],
                json.dumps(params, default=str),
                meta["n_train"],
                meta["mae"],
                meta["rmse"],
                meta["r2"],
            ),
        )
        conn.commit()
