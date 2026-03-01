from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "carbon_coach.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist yet."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trip_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT    NOT NULL,
                mode        TEXT    NOT NULL,
                distance_km REAL    NOT NULL,
                city        TEXT    NOT NULL,
                car_make    TEXT,
                car_model   TEXT,
                car_engine  TEXT,
                car_year    INTEGER,
                co2_kg      REAL    NOT NULL,
                timestamp   TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS food_logs (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      TEXT    NOT NULL,
                food_type    TEXT    NOT NULL,
                weight_grams REAL    NOT NULL,
                co2_kg       REAL    NOT NULL,
                timestamp    TEXT    NOT NULL
            )
        """)
        conn.commit()
