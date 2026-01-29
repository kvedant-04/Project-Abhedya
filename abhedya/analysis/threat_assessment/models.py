"""
Threat Assessment Data Models

Data models for threat assessment results, risk scores, and risk factors.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class ThreatLevel(str, Enum):
    """
    Threat level categories (INFORMATIONAL ONLY).
    
    These levels are advisory assessments and do NOT map to any actions.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskFactor:
    """
    Individual risk factor contributing to overall threat assessment.
    """
    factor_name: str
    factor_value: float  # Normalized value [0.0, 1.0]
    weight: float  # Weight in overall score [0.0, 1.0]
    contribution: float  # Weighted contribution to total score
    description: str  # Description of the factor
    reasoning: str  # Explanation of the factor value


@dataclass
class RiskScore:
    """
    Risk score with breakdown and uncertainty.
    """
    total_score: float  # Total risk score [0.0, 1.0]
    uncertainty: float  # Uncertainty in score [0.0, 1.0]
    confidence: float  # Confidence in assessment [0.0, 1.0]
    factors: List[RiskFactor]  # Individual risk factors
    score_breakdown: Dict[str, float]  # Breakdown by category
    lower_bound: float  # Lower confidence bound
    upper_bound: float  # Upper confidence bound


@dataclass
class ThreatAssessmentResult:
    """
    Complete threat assessment result.
    
    IMPORTANT: This is an ADVISORY ASSESSMENT ONLY.
    It does NOT recommend any actions.
    Threat level does NOT map to any action.
    """
    assessment_id: str
    timestamp: datetime
    threat_level: ThreatLevel
    risk_score: RiskScore
    threat_likelihood: float  # Probabilistic threat likelihood [0.0, 1.0]
    confidence_percentage: float  # Confidence as percentage [0.0, 100.0]
    uncertainty_percentage: float  # Uncertainty as percentage [0.0, 100.0]
    reasoning: str  # Detailed reasoning
    score_breakdown: Dict[str, Any]  # Transparent score breakdown
    advisory_statement: str = field(default="ADVISORY ASSESSMENT ONLY - No action recommendations. Threat level does not map to any action.")
    
    def __post_init__(self):
        """Validate assessment result."""
        if not 0.0 <= self.threat_likelihood <= 1.0:
            raise ValueError(f"Threat likelihood must be in [0.0, 1.0], got {self.threat_likelihood}")
        if not 0.0 <= self.confidence_percentage <= 100.0:
            raise ValueError(f"Confidence percentage must be in [0.0, 100.0], got {self.confidence_percentage}")
        if not 0.0 <= self.uncertainty_percentage <= 100.0:
            raise ValueError(f"Uncertainty percentage must be in [0.0, 100.0], got {self.uncertainty_percentage}")

