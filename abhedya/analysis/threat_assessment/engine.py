"""
Threat Assessment and Risk Scoring Engine

Multi-factor weighted risk scoring with probabilistic threat likelihood.
All assessments are ADVISORY ONLY - no action recommendations.
"""

import uuid
import math
from abhedya.domain.value_objects import Velocity
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from abhedya.analysis.threat_assessment.models import (
    ThreatAssessmentResult,
    ThreatLevel,
    RiskFactor,
    RiskScore
)
from abhedya.tracking.models import Track
from abhedya.domain.value_objects import Coordinates
from abhedya.infrastructure.config.config import (
    ThreatAssessmentThresholds,
    ProtectedAirspaceConfiguration,
    ConfidenceThresholds
)


class ThreatAssessmentEngine:
    """
    Threat assessment and risk scoring engine.
    
    STRICT RULES:
    - No binary decisions
    - No action recommendations
    - Threat level must NEVER map directly to any action
    - Output must explicitly state: "Advisory Assessment Only"
    
    Provides:
    - Multi-factor weighted risk scoring
    - Probabilistic threat likelihood
    - Confidence percentages with uncertainty bounds
    - Transparent score breakdown
    """
    
    def __init__(
        self,
        factor_weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize threat assessment engine.
        
        Args:
            factor_weights: Custom factor weights (default: use standard weights)
        """
        # Standard factor weights (must sum to 1.0)
        self.factor_weights = factor_weights or {
            "entity_classification": 0.25,  # Entity type (hostile, unknown, etc.)
            "proximity": 0.25,              # Distance to protected zones
            "behavior": 0.20,                # Behavioral patterns
            "speed": 0.15,                   # Speed characteristics
            "trajectory": 0.10,              # Trajectory analysis
            "confidence": 0.05               # Data confidence
        }
        
        # Validate weights sum to 1.0
        total_weight = sum(self.factor_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Factor weights must sum to 1.0, got {total_weight}")
    
    def assess_track(
        self,
        track: Track,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> ThreatAssessmentResult:
        """
        Assess threat level for a track.
        
        IMPORTANT: This is an ADVISORY ASSESSMENT ONLY.
        It does NOT recommend any actions.
        Threat level does NOT map to any action.
        
        Args:
            track: Track to assess
            additional_context: Additional context (optional)
            
        Returns:
            ThreatAssessmentResult with complete assessment
        """
        # Calculate risk factors
        factors = self._calculate_risk_factors(track, additional_context)
        
        # Calculate total risk score
        total_score = sum(factor.contribution for factor in factors)
        total_score = max(0.0, min(1.0, total_score))  # Clamp to [0, 1]
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(factors, track)
        
        # Calculate confidence
        confidence = self._calculate_confidence(track, factors)
        
        # Calculate threat likelihood (probabilistic)
        threat_likelihood = self._calculate_threat_likelihood(total_score, uncertainty)
        
        # Determine threat level (INFORMATIONAL ONLY)
        threat_level = self._determine_threat_level(total_score)
        
        # Calculate confidence bounds
        lower_bound, upper_bound = self._calculate_confidence_bounds(
            total_score,
            uncertainty
        )
        
        # Create score breakdown
        score_breakdown = self._create_score_breakdown(factors, total_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            track,
            factors,
            total_score,
            threat_level,
            threat_likelihood,
            confidence,
            uncertainty
        )
        
        # Create assessment result
        return ThreatAssessmentResult(
            assessment_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            threat_level=threat_level,
            risk_score=RiskScore(
                total_score=total_score,
                uncertainty=uncertainty,
                confidence=confidence,
                factors=factors,
                score_breakdown=score_breakdown,
                lower_bound=lower_bound,
                upper_bound=upper_bound
            ),
            threat_likelihood=threat_likelihood,
            confidence_percentage=confidence * 100.0,
            uncertainty_percentage=uncertainty * 100.0,
            reasoning=reasoning,
            score_breakdown=score_breakdown,
            advisory_statement="ADVISORY ASSESSMENT ONLY - No action recommendations. Threat level does not map to any action."
        )
    
    def _calculate_risk_factors(
        self,
        track: Track,
        additional_context: Optional[Dict[str, Any]]
    ) -> List[RiskFactor]:
        """Calculate all risk factors."""
        factors = []
        
        # Entity classification factor
        entity_factor = self._calculate_entity_classification_factor(track)
        factors.append(entity_factor)
        
        # Proximity factor
        proximity_factor = self._calculate_proximity_factor(track)
        factors.append(proximity_factor)
        
        # Behavior factor
        behavior_factor = self._calculate_behavior_factor(track)
        factors.append(behavior_factor)
        
        # Speed factor
        speed_factor = self._calculate_speed_factor(track)
        factors.append(speed_factor)
        
        # Trajectory factor
        trajectory_factor = self._calculate_trajectory_factor(track)
        factors.append(trajectory_factor)
        
        # Confidence factor
        confidence_factor = self._calculate_confidence_factor(track)
        factors.append(confidence_factor)
        
        return factors
    
    def _calculate_entity_classification_factor(self, track: Track) -> RiskFactor:
        """Calculate risk factor from entity classification."""
        classification = track.classification
        
        # Map object types to risk values
        type_risk_map = {
            "UNKNOWN_OBJECT": 0.6,  # Medium-high risk for unknown
            "AIRCRAFT": 0.3,  # Lower risk for known aircraft
            "AERIAL_DRONE": 0.5,  # Medium risk for drones
        }
        
        # Get base risk from object type
        object_type = classification.object_type.value
        base_risk = type_risk_map.get(object_type, 0.5)
        
        # Adjust based on classification probability and uncertainty
        # Higher uncertainty increases risk
        adjusted_risk = base_risk * (1.0 - classification.uncertainty * 0.3)
        
        # Factor value is probability-weighted
        factor_value = adjusted_risk * classification.probability
        
        weight = self.factor_weights["entity_classification"]
        contribution = factor_value * weight
        
        reasoning = (
            f"Entity type: {object_type} "
            f"(probability: {classification.probability:.2%}, "
            f"uncertainty: {classification.uncertainty:.2%})"
        )
        
        return RiskFactor(
            factor_name="Entity Classification",
            factor_value=factor_value,
            weight=weight,
            contribution=contribution,
            description="Risk based on classified entity type",
            reasoning=reasoning
        )
    
    def _calculate_proximity_factor(self, track: Track) -> RiskFactor:
        """Calculate risk factor from proximity to protected zones."""
        # Calculate distance to origin
        distance = math.sqrt(
            track.position.x**2 +
            track.position.y**2 +
            track.position.z**2
        )
        
        # Calculate proximity risk based on zones
        if distance < ProtectedAirspaceConfiguration.CRITICAL_ZONE_RADIUS_METERS:
            # In critical zone
            proximity_risk = 0.9
            zone_name = "Critical Zone"
        elif distance < ProtectedAirspaceConfiguration.PROTECTED_ZONE_RADIUS_METERS:
            # In protected zone
            proximity_risk = 0.7
            zone_name = "Protected Zone"
        elif distance < ProtectedAirspaceConfiguration.EXTENDED_ZONE_RADIUS_METERS:
            # In extended zone
            proximity_risk = 0.4
            zone_name = "Extended Zone"
        else:
            # Outside all zones
            proximity_risk = 0.1
            zone_name = "Outside Zones"
        
        # Adjust based on distance (closer = higher risk)
        if distance > 0:
            distance_factor = 1.0 - min(1.0, distance / 200000.0)  # 200 km max
            proximity_risk = proximity_risk * (0.5 + 0.5 * distance_factor)
        
        factor_value = proximity_risk
        weight = self.factor_weights["proximity"]
        contribution = factor_value * weight
        
        reasoning = (
            f"Distance: {distance/1000.0:.2f} km, "
            f"Zone: {zone_name}"
        )
        
        return RiskFactor(
            factor_name="Proximity",
            factor_value=factor_value,
            weight=weight,
            contribution=contribution,
            description="Risk based on proximity to protected zones",
            reasoning=reasoning
        )
    
    def _calculate_behavior_factor(self, track: Track) -> RiskFactor:
        """Calculate risk factor from behavioral patterns."""
        # Analyze behavior from track metadata
        metadata = track.metadata
        
        # Check for approaching behavior
        behavior_risk = 0.3  # Base risk
        
        if track.velocity:
            # Check if heading towards origin
            heading_to_origin = self._calculate_heading_to_origin(
                track.position,
                track.velocity
            )
            
            # If heading directly towards origin, higher risk
            if abs(heading_to_origin) < 30.0:  # Within 30 degrees
                behavior_risk += 0.4
            elif abs(heading_to_origin) < 60.0:
                behavior_risk += 0.2
        
        # Check for high speed (potentially aggressive behavior)
        if track.velocity:
            speed = track.velocity.speed
            if speed > ThreatAssessmentThresholds.HOSTILE_SPEED_THRESHOLD_METERS_PER_SECOND:
                behavior_risk += 0.2
        
        factor_value = min(1.0, behavior_risk)
        weight = self.factor_weights["behavior"]
        contribution = factor_value * weight
        
        reasoning = "Behavioral pattern analysis"
        if track.velocity:
            reasoning += f" (speed: {track.velocity.speed:.1f} m/s)"
        
        return RiskFactor(
            factor_name="Behavior",
            factor_value=factor_value,
            weight=weight,
            contribution=contribution,
            description="Risk based on behavioral patterns",
            reasoning=reasoning
        )
    
    def _calculate_speed_factor(self, track: Track) -> RiskFactor:
        """Calculate risk factor from speed characteristics."""
        if not track.velocity:
            return RiskFactor(
                factor_name="Speed",
                factor_value=0.0,
                weight=self.factor_weights["speed"],
                contribution=0.0,
                description="Risk based on speed characteristics",
                reasoning="No velocity data available"
            )
        
        speed = track.velocity.speed
        
        # Speed risk mapping
        if speed > ThreatAssessmentThresholds.HOSTILE_SPEED_THRESHOLD_METERS_PER_SECOND:
            speed_risk = 0.8  # High speed = higher risk
        elif speed > 200.0:
            speed_risk = 0.5  # Medium speed
        elif speed > ThreatAssessmentThresholds.CIVILIAN_SPEED_THRESHOLD_METERS_PER_SECOND:
            speed_risk = 0.3  # Lower speed
        else:
            speed_risk = 0.1  # Very low speed
        
        factor_value = speed_risk
        weight = self.factor_weights["speed"]
        contribution = factor_value * weight
        
        reasoning = f"Speed: {speed:.1f} m/s ({speed*3.6:.1f} km/h)"
        
        return RiskFactor(
            factor_name="Speed",
            factor_value=factor_value,
            weight=weight,
            contribution=contribution,
            description="Risk based on speed characteristics",
            reasoning=reasoning
        )
    
    def _calculate_trajectory_factor(self, track: Track) -> RiskFactor:
        """Calculate risk factor from trajectory analysis."""
        # Simple trajectory analysis
        trajectory_risk = 0.3  # Base risk
        
        if track.velocity:
            # Check if trajectory is towards protected zones
            heading_to_origin = self._calculate_heading_to_origin(
                track.position,
                track.velocity
            )
            
            if abs(heading_to_origin) < 45.0:
                trajectory_risk = 0.7  # Heading towards origin
            elif abs(heading_to_origin) < 90.0:
                trajectory_risk = 0.5  # Somewhat towards origin
        
        factor_value = trajectory_risk
        weight = self.factor_weights["trajectory"]
        contribution = factor_value * weight
        
        reasoning = "Trajectory analysis"
        
        return RiskFactor(
            factor_name="Trajectory",
            factor_value=factor_value,
            weight=weight,
            contribution=contribution,
            description="Risk based on trajectory analysis",
            reasoning=reasoning
        )
    
    def _calculate_confidence_factor(self, track: Track) -> RiskFactor:
        """Calculate risk factor from data confidence."""
        # Lower confidence increases uncertainty, which increases risk
        confidence = track.confidence
        
        # Invert confidence to get uncertainty risk
        # Higher uncertainty = higher risk (less certain = more risky)
        uncertainty_risk = 1.0 - confidence
        
        # Scale down (confidence is less important than other factors)
        factor_value = uncertainty_risk * 0.5
        
        weight = self.factor_weights["confidence"]
        contribution = factor_value * weight
        
        reasoning = f"Data confidence: {confidence:.2%}"
        
        return RiskFactor(
            factor_name="Confidence",
            factor_value=factor_value,
            weight=weight,
            contribution=contribution,
            description="Risk based on data confidence",
            reasoning=reasoning
        )
    
    def _calculate_heading_to_origin(
        self,
        position: Coordinates,
        velocity: Velocity
    ) -> float:
        """Calculate angle between velocity and vector to origin."""
        import math
        
        # Vector to origin
        to_origin_x = -position.x
        to_origin_y = -position.y
        
        # Velocity vector
        vel_x = velocity.vx
        vel_y = velocity.vy
        
        # Calculate angle
        dot = to_origin_x * vel_x + to_origin_y * vel_y
        mag_to_origin = math.sqrt(to_origin_x**2 + to_origin_y**2)
        mag_vel = math.sqrt(vel_x**2 + vel_y**2)
        
        if mag_to_origin == 0 or mag_vel == 0:
            return 90.0
        
        cos_angle = dot / (mag_to_origin * mag_vel)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    def _calculate_uncertainty(
        self,
        factors: List[RiskFactor],
        track: Track
    ) -> float:
        """Calculate overall uncertainty in assessment."""
        # Uncertainty from classification
        classification_uncertainty = track.classification.uncertainty
        
        # Uncertainty from data confidence
        confidence_uncertainty = 1.0 - track.confidence
        
        # Uncertainty from factor variance (if factors disagree, higher uncertainty)
        factor_values = [f.factor_value for f in factors]
        if len(factor_values) > 1:
            mean_value = sum(factor_values) / len(factor_values)
            variance = sum((v - mean_value)**2 for v in factor_values) / len(factor_values)
            factor_uncertainty = min(1.0, variance * 4.0)  # Scale variance
        else:
            factor_uncertainty = 0.0
        
        # Combined uncertainty (weighted average)
        uncertainty = (
            classification_uncertainty * 0.4 +
            confidence_uncertainty * 0.3 +
            factor_uncertainty * 0.3
        )
        
        return min(1.0, max(0.0, uncertainty))
    
    def _calculate_confidence(
        self,
        track: Track,
        factors: List[RiskFactor]
    ) -> float:
        """Calculate overall confidence in assessment."""
        # Base confidence from track confidence
        base_confidence = track.confidence
        
        # Adjust based on classification confidence
        classification_confidence = 1.0 - track.classification.uncertainty
        
        # Adjust based on data quality (more factors with data = higher confidence)
        data_quality = min(1.0, len([f for f in factors if f.factor_value > 0]) / len(factors))
        
        # Combined confidence
        confidence = (
            base_confidence * 0.5 +
            classification_confidence * 0.3 +
            data_quality * 0.2
        )
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_threat_likelihood(
        self,
        risk_score: float,
        uncertainty: float
    ) -> float:
        """
        Calculate probabilistic threat likelihood.
        
        Args:
            risk_score: Total risk score [0.0, 1.0]
            uncertainty: Assessment uncertainty [0.0, 1.0]
            
        Returns:
            Threat likelihood [0.0, 1.0]
        """
        # Base likelihood from risk score
        base_likelihood = risk_score
        
        # Adjust for uncertainty (higher uncertainty = lower likelihood)
        # But also consider that uncertainty itself is a risk factor
        uncertainty_adjustment = uncertainty * 0.2  # Uncertainty adds some risk
        
        # Combined likelihood
        likelihood = base_likelihood + uncertainty_adjustment
        
        return min(1.0, max(0.0, likelihood))
    
    def _determine_threat_level(self, risk_score: float) -> ThreatLevel:
        """
        Determine threat level from risk score (INFORMATIONAL ONLY).
        
        IMPORTANT: Threat level does NOT map to any action.
        This is purely informational.
        """
        if risk_score >= ThreatAssessmentThresholds.THREAT_LEVEL_CRITICAL_THRESHOLD:
            return ThreatLevel.CRITICAL
        elif risk_score >= ThreatAssessmentThresholds.THREAT_LEVEL_HIGH_THRESHOLD:
            return ThreatLevel.HIGH
        elif risk_score >= ThreatAssessmentThresholds.THREAT_LEVEL_MEDIUM_THRESHOLD:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_confidence_bounds(
        self,
        risk_score: float,
        uncertainty: float
    ) -> Tuple[float, float]:
        """
        Calculate confidence bounds for risk score.
        
        Args:
            risk_score: Total risk score
            uncertainty: Assessment uncertainty
            
        Returns:
            (lower_bound, upper_bound)
        """
        # Uncertainty range
        uncertainty_range = uncertainty * risk_score
        
        lower_bound = max(0.0, risk_score - uncertainty_range)
        upper_bound = min(1.0, risk_score + uncertainty_range)
        
        return (lower_bound, upper_bound)
    
    def _create_score_breakdown(
        self,
        factors: List[RiskFactor],
        total_score: float
    ) -> Dict[str, Any]:
        """Create transparent score breakdown."""
        breakdown = {
            "total_score": total_score,
            "factor_contributions": {
                factor.factor_name: {
                    "value": factor.factor_value,
                    "weight": factor.weight,
                    "contribution": factor.contribution,
                    "percentage_of_total": (factor.contribution / total_score * 100.0) if total_score > 0 else 0.0,
                    "reasoning": factor.reasoning
                }
                for factor in factors
            },
            "factor_weights": self.factor_weights.copy()
        }
        
        return breakdown
    
    def _generate_reasoning(
        self,
        track: Track,
        factors: List[RiskFactor],
        total_score: float,
        threat_level: ThreatLevel,
        threat_likelihood: float,
        confidence: float,
        uncertainty: float
    ) -> str:
        """Generate detailed reasoning for assessment."""
        reasoning_parts = []
        
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("THREAT ASSESSMENT - ADVISORY ONLY")
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("")
        reasoning_parts.append("IMPORTANT: This is an ADVISORY ASSESSMENT ONLY.")
        reasoning_parts.append("No action recommendations are provided.")
        reasoning_parts.append("Threat level does NOT map to any action.")
        reasoning_parts.append("")
        
        reasoning_parts.append(f"Threat Level: {threat_level.value} (INFORMATIONAL ONLY)")
        reasoning_parts.append(f"Risk Score: {total_score:.3f} (range: 0.0 to 1.0)")
        reasoning_parts.append(f"Threat Likelihood: {threat_likelihood:.2%}")
        reasoning_parts.append(f"Confidence: {confidence:.2%}")
        reasoning_parts.append(f"Uncertainty: {uncertainty:.2%}")
        reasoning_parts.append("")
        
        reasoning_parts.append("Score Breakdown:")
        reasoning_parts.append("-" * 60)
        for factor in factors:
            reasoning_parts.append(f"{factor.factor_name}:")
            reasoning_parts.append(f"  Value: {factor.factor_value:.3f}")
            reasoning_parts.append(f"  Weight: {factor.weight:.3f}")
            reasoning_parts.append(f"  Contribution: {factor.contribution:.3f}")
            reasoning_parts.append(f"  Reasoning: {factor.reasoning}")
            reasoning_parts.append("")
        
        reasoning_parts.append("Confidence Bounds:")
        lower, upper = self._calculate_confidence_bounds(total_score, uncertainty)
        reasoning_parts.append(f"  Lower bound: {lower:.3f}")
        reasoning_parts.append(f"  Upper bound: {upper:.3f}")
        reasoning_parts.append("")
        
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("END OF ADVISORY ASSESSMENT")
        reasoning_parts.append("=" * 60)
        
        return "\n".join(reasoning_parts)

