import sqlite3
from pathlib import Path

DB_PATH = Path("data/cars.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL,
    input_json      TEXT    NOT NULL,
    predicted_price REAL    NOT NULL,
    model_version   TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS model_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL,
    model_name  TEXT    NOT NULL,
    version     TEXT    NOT NULL,
    params_json TEXT,
    n_train     INTEGER,
    mae         REAL,
    rmse        REAL,
    r2          REAL,
    is_active   INTEGER NOT NULL DEFAULT 0
);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
