from __future__ import annotations

from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

from models.enums import TransportMode, FoodType
from models.entries import TripEntry, FoodEntry
from engine.calculator import calculate_trip, calculate_food
from engine.suggestions import generate_suggestions
from db.queries import (
    insert_trip, insert_food,
    get_daily_total,
    biggest_transport_today, biggest_food_today,
    get_weekly_summary, get_monthly_summary, get_yearly_summary,
)

router = APIRouter()


# --- Request bodies ---

class TripRequest(BaseModel):
    user_id: str
    mode: TransportMode
    distance_km: float
    city: str
    car_make: str | None = None    # e.g. "volvo"   — only needed when mode is "car"
    car_model: str | None = None   # e.g. "xc60"
    car_engine: str | None = None  # e.g. "petrol", "diesel", "hybrid", "plug_in_hybrid", "electric"
    car_year: int | None = None    # e.g. 2022

    @field_validator("distance_km")
    @classmethod
    def distance_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("distance_km must be greater than 0")
        return v


class FoodRequest(BaseModel):
    user_id: str
    food_type: FoodType
    weight_grams: float

    @field_validator("weight_grams")
    @classmethod
    def weight_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("weight_grams must be greater than 0")
        return v


# --- Endpoints ---

@router.post("/log/trip")
def log_trip(body: TripRequest):
    co2 = calculate_trip(
        body.mode, body.distance_km,
        body.car_make, body.car_model, body.car_engine, body.car_year,
    )
    entry = TripEntry(
        user_id=body.user_id, mode=body.mode, distance_km=body.distance_km,
        city=body.city, car_make=body.car_make, car_model=body.car_model,
        car_engine=body.car_engine, car_year=body.car_year, co2_kg=co2,
    )
    insert_trip(entry)
    return {"user_id": body.user_id, "co2_kg": co2, "mode": body.mode,
            "car_make": body.car_make, "car_model": body.car_model,
            "car_engine": body.car_engine, "car_year": body.car_year}


@router.post("/log/food")
def log_food(body: FoodRequest):
    co2 = calculate_food(body.food_type, body.weight_grams)
    entry = FoodEntry(
        user_id=body.user_id, food_type=body.food_type,
        weight_grams=body.weight_grams, co2_kg=co2,
    )
    insert_food(entry)
    return {"user_id": body.user_id, "co2_kg": co2, "food_type": body.food_type}


@router.get("/summary/today")
def summary_today(user_id: str):
    total = get_daily_total(user_id, date.today())
    return {"user_id": user_id, "date": date.today().isoformat(), "total_co2_kg": total}


@router.get("/suggestions")
def suggestions(user_id: str):
    today = date.today()
    total = get_daily_total(user_id, today)
    transport = biggest_transport_today(user_id, today)
    food = biggest_food_today(user_id, today)
    tips = generate_suggestions(transport, food, total)
    return {"user_id": user_id, "tips": tips}


@router.get("/summary/week")
def summary_week(user_id: str):
    data = get_weekly_summary(user_id)
    return {"user_id": user_id, **data}


@router.get("/summary/month")
def summary_month(user_id: str):
    data = get_monthly_summary(user_id)
    return {"user_id": user_id, **data}


@router.get("/summary/year")
def summary_year(user_id: str):
    data = get_yearly_summary(user_id)
    return {"user_id": user_id, **data}
