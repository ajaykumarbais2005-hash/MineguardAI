from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    score: float
    level: str
    severity: float
    likelihood: float
    exposure: float
    recurrence: float
    reason: str
    recommended_action: str


def calculate_risk(severity: float, likelihood: float, exposure: float, recurrence: float) -> RiskResult:
    factors = (severity, likelihood, exposure, recurrence)
    if any(factor < 1 or factor > 5 for factor in factors):
        raise ValueError("Risk factors must be between 1 and 5")
    raw_score = severity * likelihood * exposure * recurrence
    score = round((raw_score / 625) * 100, 2)
    level = "LOW" if score <= 25 else "MEDIUM" if score <= 50 else "HIGH" if score <= 75 else "CRITICAL"
    reason = f"Score reflects severity {severity}, likelihood {likelihood}, exposure {exposure}, and recurrence {recurrence}."
    actions = {"LOW": "Continue routine controls and scheduled monitoring.", "MEDIUM": "Review controls and increase monitoring frequency.", "HIGH": "Assign immediate corrective action and verify controls.", "CRITICAL": "Stop affected work, escalate, and verify controls before restart."}
    return RiskResult(score, level, severity, likelihood, exposure, recurrence, reason, actions[level])
