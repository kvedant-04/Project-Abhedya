"""
Intent Probability Inference Engine

Probabilistic intent assessment using explainable, rule-based logic.
All outputs are ADVISORY ONLY - no action recommendations.

STRICT RULES:
- No binary decisions
- No action recommendations
- Intent probabilities do NOT map to any actions
- Explainable rule-based logic only (NO deep learning)
- Probabilities must sum to ≤ 100%
- Fail-safe to MONITORING_ONLY if inputs missing
"""

from abhedya.analysis.intent_inference.engine import IntentInferenceEngine
from abhedya.analysis.intent_inference.models import (
    IntentProbabilityResult,
    IntentCategory
)

__all__ = [
    "IntentInferenceEngine",
    "IntentProbabilityResult",
    "IntentCategory",
]

