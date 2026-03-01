from __future__ import annotations

from models.enums import TransportMode, FoodType
from data.emission_factors import TRANSPORT_FACTORS, FOOD_FACTORS, CAR_EMISSION_FACTORS


def _car_factor(make: str, model: str, engine: str, year: int) -> float:
    """Return kg CO2/km for a specific car variant.

    Fallback chain:
      1. Exact make + model + engine + year
      2. Nearest available year for that make + model + engine
      3. Average car factor
    """
    year_data = (
        CAR_EMISSION_FACTORS
        .get(make.lower(), {})
        .get(model.lower(), {})
        .get(engine.lower(), {})
    )
    if not year_data:
        return TRANSPORT_FACTORS.get("car", 0.21)

    if year in year_data:
        return year_data[year]

    # Nearest year fallback
    nearest = min(year_data.keys(), key=lambda y: abs(y - year))
    return year_data[nearest]


def calculate_trip(
    mode: TransportMode,
    distance_km: float,
    car_make: str | None = None,
    car_model: str | None = None,
    car_engine: str | None = None,
    car_year: int | None = None,
) -> float:
    """Return kg CO2 produced by a single trip.

    For CAR trips, supply car_make, car_model, car_engine, and car_year
    to get a model-specific emission figure.
    Falls back to the average petrol car factor if any detail is missing.
    """
    if mode == TransportMode.CAR and car_make and car_model and car_engine and car_year:
        factor = _car_factor(car_make, car_model, car_engine, car_year)
    else:
        factor = TRANSPORT_FACTORS.get(mode.value, 0.0)
    return round(factor * distance_km, 4)


def calculate_food(food_type: FoodType, weight_grams: float) -> float:
    """Return kg CO2 produced by a food entry."""
    factor = FOOD_FACTORS.get(food_type.value, 0.0)
    return round(factor * (weight_grams / 1000), 4)


def daily_total(trip_emissions: list[float], food_emissions: list[float]) -> float:
    """Return total kg CO2 for the day across all trips and food."""
    return round(sum(trip_emissions) + sum(food_emissions), 4)
