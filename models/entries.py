from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from models.enums import TransportMode, FoodType


@dataclass
class TripEntry:
    """A single logged journey."""
    user_id: str
    mode: TransportMode
    distance_km: float
    city: str
    car_make: str | None = None    # e.g. "volvo"   — only used when mode is CAR
    car_model: str | None = None   # e.g. "xc60"
    car_engine: str | None = None  # e.g. "petrol", "diesel", "hybrid", "plug_in_hybrid", "electric"
    car_year: int | None = None    # e.g. 2022
    timestamp: datetime = field(default_factory=datetime.now)
    co2_kg: float = 0.0


@dataclass
class FoodEntry:
    """A single logged meal or food item."""
    user_id: str
    food_type: FoodType
    weight_grams: float
    timestamp: datetime = field(default_factory=datetime.now)
    co2_kg: float = 0.0
