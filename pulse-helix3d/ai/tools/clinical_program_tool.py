"""Clinical program selection tool."""
from __future__ import annotations

from typing import Dict

PROGRAMS = {
    "metabolic": "Metabolic Guard",
    "sleep": "Circadian Elite",
    "cardio": "CardioMetabolic Precision",
}


def select_program(goal: str) -> Dict[str, str]:
    match = PROGRAMS.get(goal, "Metabolic Guard")
    return {"goal": goal, "program": match}
