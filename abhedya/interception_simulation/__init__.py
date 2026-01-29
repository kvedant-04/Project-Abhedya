"""
Interception Feasibility Simulation Engine

Provides:
- Relative motion and geometry analysis
- Time-to-closest-approach estimation
- Probabilistic feasibility assessment
- Risk envelope evaluation

STRICT CONSTRAINTS:
- Mathematical feasibility analysis only
- No missile, interceptor, or guidance modeling
- No control laws
- No execution timelines
- No optimal intercept vectors

All outputs are mathematical feasibility assessments only.
"""

from abhedya.interception_simulation.feasibility import InterceptionFeasibilityAnalyzer
from abhedya.interception_simulation.geometry import GeometryAnalyzer
from abhedya.interception_simulation.risk_envelope import RiskEnvelopeEvaluator
from abhedya.interception_simulation.models import (
    InterceptionFeasibilityResult,
    GeometryAnalysisResult,
    ClosestApproachResult,
    RiskEnvelopeResult
)

__all__ = [
    "InterceptionFeasibilityAnalyzer",
    "GeometryAnalyzer",
    "RiskEnvelopeEvaluator",
    "InterceptionFeasibilityResult",
    "GeometryAnalysisResult",
    "ClosestApproachResult",
    "RiskEnvelopeResult",
]

