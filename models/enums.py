from __future__ import annotations

from enum import Enum


class TransportMode(str, Enum):
    """Transport options and their associated carbon impact.

    Distance is measured in kilometres.
    """
    CAR = "car"
    BUS = "bus"
    SUBWAY = "subway"
    WALK = "walk"
    BIKE = "bike"


class FoodType(str, Enum):
    """Food categories and their associated carbon impact.

    Weight is measured in grams.
    """
    BEEF = "beef"
    CHICKEN = "chicken"
    PORK = "pork"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
