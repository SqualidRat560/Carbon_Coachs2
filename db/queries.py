from __future__ import annotations

from datetime import date, datetime, timedelta

from db.database import get_connection
from models.entries import TripEntry, FoodEntry
from models.enums import TransportMode, FoodType


# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------

def insert_trip(entry: TripEntry) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO trip_logs
                (user_id, mode, distance_km, city,
                 car_make, car_model, car_engine, car_year,
                 co2_kg, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.user_id, entry.mode.value, entry.distance_km, entry.city,
                entry.car_make, entry.car_model, entry.car_engine, entry.car_year,
                entry.co2_kg, entry.timestamp.isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid


def insert_food(entry: FoodEntry) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO food_logs
                (user_id, food_type, weight_grams, co2_kg, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entry.user_id, entry.food_type.value, entry.weight_grams,
                entry.co2_kg, entry.timestamp.isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Range helpers
# ---------------------------------------------------------------------------

def _range_bounds(start: date, end: date) -> tuple[str, str]:
    return (
        datetime(start.year, start.month, start.day, 0, 0, 0).isoformat(),
        datetime(end.year, end.month, end.day, 23, 59, 59).isoformat(),
    )


def _total_in_range(user_id: str, start: date, end: date) -> float:
    s, e = _range_bounds(start, end)
    with get_connection() as conn:
        trips = conn.execute(
            "SELECT COALESCE(SUM(co2_kg), 0) FROM trip_logs WHERE user_id=? AND timestamp BETWEEN ? AND ?",
            (user_id, s, e),
        ).fetchone()[0]
        foods = conn.execute(
            "SELECT COALESCE(SUM(co2_kg), 0) FROM food_logs WHERE user_id=? AND timestamp BETWEEN ? AND ?",
            (user_id, s, e),
        ).fetchone()[0]
    return round(trips + foods, 4)


def _daily_totals_in_range(user_id: str, start: date, end: date) -> dict[str, float]:
    """Return {date_str: co2_kg} for every day in the range."""
    totals: dict[str, float] = {}
    current = start
    while current <= end:
        totals[current.isoformat()] = _total_in_range(user_id, current, current)
        current += timedelta(days=1)
    return totals


# ---------------------------------------------------------------------------
# Today
# ---------------------------------------------------------------------------

def get_daily_total(user_id: str, day: date) -> float:
    return _total_in_range(user_id, day, day)


def biggest_transport_today(user_id: str, day: date) -> TransportMode | None:
    s, e = _range_bounds(day, day)
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT mode, SUM(co2_kg) as total FROM trip_logs WHERE user_id=? AND timestamp BETWEEN ? AND ? GROUP BY mode ORDER BY total DESC LIMIT 1",
            (user_id, s, e),
        ).fetchone()
    return TransportMode(rows["mode"]) if rows else None


def biggest_food_today(user_id: str, day: date) -> FoodType | None:
    s, e = _range_bounds(day, day)
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT food_type, SUM(co2_kg) as total FROM food_logs WHERE user_id=? AND timestamp BETWEEN ? AND ? GROUP BY food_type ORDER BY total DESC LIMIT 1",
            (user_id, s, e),
        ).fetchone()
    return FoodType(rows["food_type"]) if rows else None


# ---------------------------------------------------------------------------
# Weekly summary (last 7 days)
# ---------------------------------------------------------------------------

def get_weekly_summary(user_id: str) -> dict:
    today = date.today()
    start = today - timedelta(days=6)
    daily = _daily_totals_in_range(user_id, start, today)
    total = round(sum(daily.values()), 4)
    days_with_data = sum(1 for v in daily.values() if v > 0)
    avg = round(total / days_with_data, 4) if days_with_data else 0.0
    return {
        "period": f"{start.isoformat()} to {today.isoformat()}",
        "total_co2_kg": total,
        "daily_average_co2_kg": avg,
        "daily_breakdown": daily,
    }


# ---------------------------------------------------------------------------
# Monthly summary (current calendar month)
# ---------------------------------------------------------------------------

def get_monthly_summary(user_id: str) -> dict:
    today = date.today()
    start = today.replace(day=1)
    daily = _daily_totals_in_range(user_id, start, today)
    total = round(sum(daily.values()), 4)
    days_with_data = sum(1 for v in daily.values() if v > 0)
    avg = round(total / days_with_data, 4) if days_with_data else 0.0
    return {
        "period": f"{start.isoformat()} to {today.isoformat()}",
        "total_co2_kg": total,
        "daily_average_co2_kg": avg,
        "daily_breakdown": daily,
    }


# ---------------------------------------------------------------------------
# Yearly summary (current calendar year)
# ---------------------------------------------------------------------------

def get_yearly_summary(user_id: str) -> dict:
    today = date.today()
    start = today.replace(month=1, day=1)

    # Build monthly totals
    monthly: dict[str, float] = {}
    year = today.year
    for month in range(1, today.month + 1):
        month_start = date(year, month, 1)
        if month < today.month:
            # last day of the month
            next_month = date(year, month + 1, 1)
            month_end = next_month - timedelta(days=1)
        else:
            month_end = today
        monthly[month_start.strftime("%Y-%m")] = _total_in_range(user_id, month_start, month_end)

    total = round(sum(monthly.values()), 4)
    months_with_data = sum(1 for v in monthly.values() if v > 0)
    avg = round(total / months_with_data, 4) if months_with_data else 0.0
    return {
        "period": f"{start.isoformat()} to {today.isoformat()}",
        "total_co2_kg": total,
        "monthly_average_co2_kg": avg,
        "monthly_breakdown": monthly,
    }
