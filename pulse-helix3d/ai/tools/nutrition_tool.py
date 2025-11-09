"""Nutrition calculation helpers."""
from __future__ import annotations

from typing import Dict


MICRO_DEFAULTS = {
    "iron": 18,
    "vitamin_c": 90,
    "magnesium": 420,
}


def calculate_macros(calories: int, protein_ratio: int, fat_ratio: int, carb_ratio: int) -> Dict[str, float]:
    total_ratio = protein_ratio + fat_ratio + carb_ratio
    return {
        "protein_g": calories * (protein_ratio / total_ratio) / 4,
        "fat_g": calories * (fat_ratio / total_ratio) / 9,
        "carb_g": calories * (carb_ratio / total_ratio) / 4,
        "micros": MICRO_DEFAULTS,
    }
