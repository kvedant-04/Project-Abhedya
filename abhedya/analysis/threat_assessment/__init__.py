"""
Threat Assessment and Risk Scoring Engine

Provides:
- Multi-factor weighted risk scoring
- Probabilistic threat likelihood output
- Confidence percentages with uncertainty bounds
- Threat categories: Low, Medium, High, Critical (INFORMATIONAL ONLY)
- Transparent score breakdown

STRICT RULES:
- No binary decisions
- No action recommendations
- Threat level must NEVER map directly to any action
- Output must explicitly state: "Advisory Assessment Only"
"""

from abhedya.analysis.threat_assessment.engine import ThreatAssessmentEngine
from abhedya.analysis.threat_assessment.models import (
    ThreatAssessmentResult,
    ThreatLevel,
    RiskFactor,
    RiskScore
)

__all__ = [
    "ThreatAssessmentEngine",
    "ThreatAssessmentResult",
    "ThreatLevel",
    "RiskFactor",
    "RiskScore",
]
