"""
Decision, Ethics, and Human-in-the-Loop Engine

Provides:
- Aggregation of advisory outputs
- Enforcement of ethical and legal constraints
- Enforcement of protected and civilian airspace rules
- Explicit human review state requirements
- NO_ACTION default under uncertainty

CRITICAL: This engine SHALL NOT output executable commands.
It only outputs advisory system states.

System Modes:
- Advisory Recommendation Mode
- Human Approval Required Mode
- Monitoring Only Mode
- Degraded Safe Mode
"""

from abhedya.decision.engine import DecisionEngine
from abhedya.decision.models import (
    SystemMode,
    AdvisorySystemState,
    HumanReviewState,
    DecisionResult
)

__all__ = [
    "DecisionEngine",
    "SystemMode",
    "AdvisorySystemState",
    "HumanReviewState",
    "DecisionResult",
]

