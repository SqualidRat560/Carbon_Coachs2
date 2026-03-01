from __future__ import annotations

from models.enums import TransportMode, FoodType
from data.emission_factors import DAILY_TARGET_KG


_TRANSPORT_TIPS: dict[TransportMode, str] = {
    TransportMode.CAR: (
        "You drove today. Try swapping one car trip for the bus or subway "
        "— it can cut transport emissions by up to 60%."
    ),
    TransportMode.BUS: (
        "Good choice using the bus. If a subway route is available, "
        "it produces even less CO2."
    ),
    TransportMode.SUBWAY: "Great — the subway is one of the lowest-emission ways to travel.",
    TransportMode.BIKE: "Cycling produces zero emissions. Keep it up!",
    TransportMode.WALK: "Walking produces zero emissions. Excellent choice.",
}

_FOOD_TIPS: dict[FoodType, str] = {
    FoodType.BEEF: (
        "Beef has the highest carbon cost of any common food. "
        "Swapping one beef meal for chicken saves around 20 kg CO2."
    ),
    FoodType.PORK: (
        "Pork is a high-emission meat. Consider chicken or a vegetarian "
        "option to lower your food footprint."
    ),
    FoodType.CHICKEN: (
        "Chicken is a lower-emission meat choice. "
        "A vegetarian option would reduce your footprint further."
    ),
    FoodType.VEGETARIAN: "Great food choice — vegetarian meals are low in carbon emissions.",
    FoodType.VEGAN: "Vegan meals have the lowest carbon footprint. Excellent!",
}


def generate_suggestions(
    biggest_transport: TransportMode | None,
    biggest_food: FoodType | None,
    total_co2: float,
) -> list[str]:
    """Return a list of personalised tip strings based on the day's activity."""
    tips: list[str] = []

    if total_co2 > DAILY_TARGET_KG:
        tips.append(
            f"Your total today is {total_co2:.2f} kg CO2, "
            f"above the {DAILY_TARGET_KG} kg daily target. "
            "Here are some ways to improve tomorrow:"
        )
    else:
        tips.append(
            f"Well done — you came in at {total_co2:.2f} kg CO2, "
            f"under the {DAILY_TARGET_KG} kg daily target."
        )

    if biggest_transport is not None:
        tips.append(_TRANSPORT_TIPS[biggest_transport])

    if biggest_food is not None:
        tips.append(_FOOD_TIPS[biggest_food])

    return tips
