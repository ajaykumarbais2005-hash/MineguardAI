from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    present: bool


def simulate_ppe_detection(case: str) -> list[Detection]:
    random = Random(case)
    helmet_present = case not in {"no_helmet", "no_helmet_no_vest"}
    vest_present = case != "no_helmet_no_vest"
    return [
        Detection("person", round(0.94 + random.random() * 0.04, 2), True),
        Detection("helmet", round(0.91 + random.random() * 0.06, 2), helmet_present),
        Detection("vest", round(0.89 + random.random() * 0.08, 2), vest_present),
        Detection("no_helmet", round(0.90 + random.random() * 0.07, 2), not helmet_present),
        Detection("no_vest", round(0.90 + random.random() * 0.07, 2), not vest_present),
    ]


def classify_event(detections: list[Detection]) -> tuple[str, str]:
    missing = {item.label for item in detections if item.label in {"no_helmet", "no_vest"} and item.present}
    if {"no_helmet", "no_vest"} <= missing:
        return "PPE_NON_COMPLIANCE", "CRITICAL"
    if missing:
        return "PPE_NON_COMPLIANCE", "HIGH"
    return "PPE_COMPLIANT", "LOW"
