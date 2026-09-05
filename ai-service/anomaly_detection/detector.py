from dataclasses import dataclass


@dataclass(frozen=True)
class AnomalyResult:
    metric: str
    value: float
    threshold: float
    is_anomaly: bool
    severity: float
    likelihood: float
    exposure: float
    recurrence: float
    reason: str


METRIC_RULES = {
    "gas_level": (25.0, "above"),
    "temperature": (42.0, "above"),
    "dust": (4.0, "above"),
    "vehicle_speed": (40.0, "above"),
    "production": (20.0, "below"),
    "inspection_frequency": (1.0, "below"),
    "violation_frequency": (5.0, "above"),
    "contractor_performance": (75.0, "below"),
}


def detect_anomaly(metric: str, value: float, threshold: float | None = None) -> AnomalyResult:
    if metric not in METRIC_RULES:
        raise ValueError(f"Unsupported anomaly metric: {metric}")
    default_threshold, direction = METRIC_RULES[metric]
    limit = default_threshold if threshold is None else threshold
    is_anomaly = value > limit if direction == "above" else value < limit
    severity = 4.0 if is_anomaly else 1.0
    likelihood = 4.0 if is_anomaly else 1.0
    exposure = 4.0 if metric in {"gas_level", "temperature", "dust", "vehicle_speed"} else 3.0
    recurrence = 3.0 if is_anomaly else 1.0
    comparison = "above" if direction == "above" else "below"
    reason = f"{metric} reading {value} is {comparison} the demo threshold {limit}." if is_anomaly else f"{metric} reading {value} is within the demo threshold {limit}."
    return AnomalyResult(metric, value, limit, is_anomaly, severity, likelihood, exposure, recurrence, reason)
