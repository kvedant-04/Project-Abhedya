"""
Interception Feasibility Simulation Data Models

Data models for feasibility analysis results.
All outputs are mathematical feasibility assessments only.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from abhedya.domain.value_objects import Coordinates, Velocity


class FeasibilityLevel(str, Enum):
    """
    Feasibility level (mathematical assessment only).
    
    These levels indicate mathematical feasibility, not recommendations.
    """
    NOT_FEASIBLE = "NOT_FEASIBLE"        # Mathematically not feasible
    MARGINALLY_FEASIBLE = "MARGINALLY_FEASIBLE"  # Borderline feasibility
    FEASIBLE = "FEASIBLE"                 # Mathematically feasible
    HIGHLY_FEASIBLE = "HIGHLY_FEASIBLE"   # Highly feasible


@dataclass
class ClosestApproachResult:
    """
    Time-to-closest-approach estimation result.
    
    Mathematical analysis only - no execution timelines.
    """
    time_to_closest_approach_seconds: float
    closest_approach_distance_meters: float
    closest_approach_position: Coordinates
    relative_velocity_at_approach: Velocity
    confidence: float  # Confidence in estimation [0.0, 1.0]
    uncertainty: float  # Uncertainty in estimation [0.0, 1.0]
    calculation_method: str  # Method used for calculation


@dataclass
class GeometryAnalysisResult:
    """
    Relative motion and geometry analysis result.
    
    Mathematical analysis only - no control laws or guidance.
    """
    relative_position: Coordinates
    relative_velocity: Velocity
    closing_velocity: float  # Velocity component along line of sight (m/s)
    range_rate: float  # Rate of change of range (m/s)
    bearing_angle_degrees: float  # Bearing angle from defender to target
    elevation_angle_degrees: float  # Elevation angle
    line_of_sight_vector: Coordinates  # Unit vector along line of sight
    relative_speed: float  # Relative speed magnitude (m/s)
    geometry_parameters: Dict[str, float]  # Additional geometry parameters


@dataclass
class RiskEnvelopeResult:
    """
    Risk envelope evaluation result.
    
    Mathematical assessment of risk envelope only.
    """
    envelope_radius_meters: float
    current_distance_meters: float
    is_within_envelope: bool
    time_to_envelope_seconds: Optional[float]  # None if not approaching
    envelope_penetration_probability: float  # Probability of envelope penetration [0.0, 1.0]
    risk_level: str  # Risk level assessment
    confidence: float  # Confidence in assessment [0.0, 1.0]


@dataclass
class InterceptionFeasibilityResult:
    """
    Complete interception feasibility assessment result.
    
    IMPORTANT: This is a MATHEMATICAL FEASIBILITY ASSESSMENT ONLY.
    It does NOT provide:
    - Missile or interceptor modeling
    - Control laws
    - Execution timelines
    - Optimal intercept vectors
    - Action recommendations
    
    It only assesses whether interception is mathematically feasible.
    """
    result_id: str
    timestamp: datetime
    feasibility_level: FeasibilityLevel
    feasibility_probability: float  # Probability of feasibility [0.0, 1.0]
    geometry_analysis: GeometryAnalysisResult
    closest_approach: ClosestApproachResult
    risk_envelope: RiskEnvelopeResult
    confidence: float  # Overall confidence [0.0, 1.0]
    uncertainty: float  # Overall uncertainty [0.0, 1.0]
    reasoning: str  # Detailed reasoning
    mathematical_assessment_only: str = "MATHEMATICAL FEASIBILITY ASSESSMENT ONLY - No missile, interceptor, or guidance modeling. No control laws. No execution timelines. No optimal intercept vectors. No action recommendations."

