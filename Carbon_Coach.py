# Carbon Coach - Main Entry Point
from __future__ import annotations

from models.enums import TransportMode, FoodType
from models.entries import TripEntry, FoodEntry
from engine.calculator import calculate_trip, calculate_food, daily_total
from engine.suggestions import generate_suggestions


def main():
    print("Carbon Coach running.")


if __name__ == "__main__":
    main()

