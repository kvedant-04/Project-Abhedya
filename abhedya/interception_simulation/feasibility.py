"""
Interception Feasibility Assessment

Probabilistic feasibility assessment using mathematical analysis only.
No missile, interceptor, or guidance modeling.
No control laws or execution timelines.
"""

import math
from datetime import datetime
import uuid
from typing import Optional, Tuple

from abhedya.interception_simulation.models import (
    InterceptionFeasibilityResult,
    FeasibilityLevel,
    ClosestApproachResult
)
from abhedya.interception_simulation.geometry import GeometryAnalyzer
from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.infrastructure.config.config import ConfidenceThresholds


class InterceptionFeasibilityAnalyzer:
    """
    Analyzes interception feasibility using mathematical analysis only.
    
    STRICT CONSTRAINTS:
    - Mathematical feasibility analysis only
    - No missile, interceptor, or guidance modeling
    - No control laws
    - No execution timelines
    - No optimal intercept vectors
    
    Provides probabilistic feasibility assessment based on geometry and motion.
    """
    
    def __init__(
        self,
        minimum_feasible_range_meters: float = 1000.0,  # 1 km minimum
        maximum_feasible_range_meters: float = 200000.0,  # 200 km maximum
        maximum_feasible_relative_speed: float = 1000.0  # 1000 m/s maximum
    ):
        """
        Initialize feasibility analyzer.
        
        Args:
            minimum_feasible_range_meters: Minimum range for feasibility
            maximum_feasible_range_meters: Maximum range for feasibility
            maximum_feasible_relative_speed: Maximum relative speed for feasibility
        """
        self.min_range = minimum_feasible_range_meters
        self.max_range = maximum_feasible_range_meters
        self.max_relative_speed = maximum_feasible_relative_speed
        self.geometry_analyzer = GeometryAnalyzer()
    
    def assess_feasibility(
        self,
        defender_position: Coordinates,
        defender_velocity: Velocity,
        target_position: Coordinates,
        target_velocity: Velocity,
        additional_constraints: Optional[dict] = None
    ) -> InterceptionFeasibilityResult:
        """
        Assess interception feasibility.
        
        IMPORTANT: This is MATHEMATICAL FEASIBILITY ASSESSMENT ONLY.
        It does NOT provide:
        - Missile or interceptor modeling
        - Control laws
        - Execution timelines
        - Optimal intercept vectors
        - Action recommendations
        
        Args:
            defender_position: Defender position
            defender_velocity: Defender velocity
            target_position: Target position
            target_velocity: Target velocity
            additional_constraints: Additional constraints (optional)
            
        Returns:
            InterceptionFeasibilityResult
        """
        # Analyze geometry and relative motion
        geometry = self.geometry_analyzer.analyze_relative_motion(
            defender_position,
            defender_velocity,
            target_position,
            target_velocity
        )
        
        # Calculate time to closest approach
        time_to_ca = self.geometry_analyzer.calculate_time_to_closest_approach(
            geometry.relative_position,
            geometry.relative_velocity
        )
        
        # Calculate closest approach distance
        ca_distance = self.geometry_analyzer.calculate_closest_approach_distance(
            geometry.relative_position,
            geometry.relative_velocity,
            time_to_ca
        )
        
        # Calculate closest approach position
        ca_position = self.geometry_analyzer.calculate_closest_approach_position(
            defender_position,
            geometry.relative_position,
            geometry.relative_velocity,
            time_to_ca
        )
        
        # Relative velocity at closest approach (same as current, constant velocity model)
        ca_relative_velocity = geometry.relative_velocity
        
        # Create closest approach result
        closest_approach = ClosestApproachResult(
            time_to_closest_approach_seconds=max(0.0, time_to_ca),  # Only future times
            closest_approach_distance_meters=ca_distance,
            closest_approach_position=ca_position,
            relative_velocity_at_approach=ca_relative_velocity,
            confidence=self._calculate_confidence(geometry, time_to_ca),
            uncertainty=self._calculate_uncertainty(geometry, time_to_ca),
            calculation_method="Constant velocity model"
        )
        
        # Assess feasibility
        feasibility_level, feasibility_probability = self._assess_feasibility_level(
            geometry,
            closest_approach,
            additional_constraints
        )
        
        # Calculate overall confidence and uncertainty
        confidence = (closest_approach.confidence + (1.0 - closest_approach.uncertainty)) / 2.0
        uncertainty = closest_approach.uncertainty
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            geometry,
            closest_approach,
            feasibility_level,
            feasibility_probability
        )
        
        # Risk envelope (simplified - would need actual risk envelope definition)
        from abhedya.interception_simulation.risk_envelope import RiskEnvelopeEvaluator
        risk_envelope_evaluator = RiskEnvelopeEvaluator()
        risk_envelope = risk_envelope_evaluator.evaluate_envelope(
            defender_position,
            target_position,
            target_velocity,
            envelope_radius_meters=50000.0  # Default 50 km
        )
        
        return InterceptionFeasibilityResult(
            result_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            feasibility_level=feasibility_level,
            feasibility_probability=feasibility_probability,
            geometry_analysis=geometry,
            closest_approach=closest_approach,
            risk_envelope=risk_envelope,
            confidence=confidence,
            uncertainty=uncertainty,
            reasoning=reasoning,
            mathematical_assessment_only="MATHEMATICAL FEASIBILITY ASSESSMENT ONLY - No missile, interceptor, or guidance modeling. No control laws. No execution timelines. No optimal intercept vectors. No action recommendations."
        )
    
    def _assess_feasibility_level(
        self,
        geometry,
        closest_approach: ClosestApproachResult,
        additional_constraints: Optional[dict]
    ) -> Tuple[FeasibilityLevel, float]:
        """
        Assess feasibility level and probability.
        
        Returns:
            (FeasibilityLevel, probability)
        """
        feasibility_score = 0.0
        
        # Range factor
        current_range = math.sqrt(
            geometry.relative_position.x**2 +
            geometry.relative_position.y**2 +
            geometry.relative_position.z**2
        )
        
        if self.min_range <= current_range <= self.max_range:
            # Within feasible range
            range_factor = 1.0 - abs(current_range - (self.min_range + self.max_range) / 2.0) / self.max_range
            range_factor = max(0.0, min(1.0, range_factor))
            feasibility_score += range_factor * 0.3
        else:
            # Outside feasible range
            feasibility_score += 0.0
        
        # Closest approach distance factor
        if closest_approach.closest_approach_distance_meters < self.min_range:
            # Will pass very close
            ca_factor = 0.9
        elif closest_approach.closest_approach_distance_meters < self.max_range:
            # Will pass within range
            ca_factor = 0.5 + 0.4 * (1.0 - closest_approach.closest_approach_distance_meters / self.max_range)
        else:
            # Will not pass within range
            ca_factor = 0.1
        
        feasibility_score += ca_factor * 0.4
        
        # Relative speed factor
        if geometry.relative_speed <= self.max_relative_speed:
            speed_factor = 1.0 - (geometry.relative_speed / self.max_relative_speed) * 0.5
            feasibility_score += speed_factor * 0.2
        else:
            # Too fast
            feasibility_score += 0.0
        
        # Closing velocity factor (positive closing = approaching)
        if geometry.closing_velocity > 0:
            # Approaching
            closing_factor = min(1.0, geometry.closing_velocity / 100.0)
            feasibility_score += closing_factor * 0.1
        else:
            # Departing
            feasibility_score += 0.0
        
        # Clamp to [0, 1]
        feasibility_score = max(0.0, min(1.0, feasibility_score))
        
        # Map to feasibility level
        if feasibility_score >= 0.8:
            level = FeasibilityLevel.HIGHLY_FEASIBLE
        elif feasibility_score >= 0.6:
            level = FeasibilityLevel.FEASIBLE
        elif feasibility_score >= 0.4:
            level = FeasibilityLevel.MARGINALLY_FEASIBLE
        else:
            level = FeasibilityLevel.NOT_FEASIBLE
        
        return (level, feasibility_score)
    
    def _calculate_confidence(
        self,
        geometry,
        time_to_ca: float
    ) -> float:
        """Calculate confidence in feasibility assessment."""
        # Confidence decreases with distance
        current_range = math.sqrt(
            geometry.relative_position.x**2 +
            geometry.relative_position.y**2 +
            geometry.relative_position.z**2
        )
        distance_factor = 1.0 - min(1.0, current_range / self.max_range)
        
        # Confidence decreases with time to closest approach (further in future = less certain)
        time_factor = 1.0 / (1.0 + abs(time_to_ca) / 3600.0)  # 1 hour scale
        
        # Confidence decreases with relative speed (faster = less certain)
        speed_factor = 1.0 - min(1.0, geometry.relative_speed / self.max_relative_speed)
        
        confidence = (distance_factor * 0.5 + time_factor * 0.3 + speed_factor * 0.2)
        
        return max(0.0, min(1.0, confidence))
    
    def _calculate_uncertainty(
        self,
        geometry,
        time_to_ca: float
    ) -> float:
        """Calculate uncertainty in feasibility assessment."""
        # Uncertainty increases with distance
        current_range = math.sqrt(
            geometry.relative_position.x**2 +
            geometry.relative_position.y**2 +
            geometry.relative_position.z**2
        )
        distance_uncertainty = min(1.0, current_range / self.max_range)
        
        # Uncertainty increases with time to closest approach
        time_uncertainty = min(1.0, abs(time_to_ca) / 3600.0)  # 1 hour scale
        
        # Uncertainty increases with relative speed
        speed_uncertainty = min(1.0, geometry.relative_speed / self.max_relative_speed)
        
        uncertainty = (distance_uncertainty * 0.4 + time_uncertainty * 0.4 + speed_uncertainty * 0.2)
        
        return max(0.0, min(1.0, uncertainty))
    
    def _generate_reasoning(
        self,
        geometry,
        closest_approach: ClosestApproachResult,
        feasibility_level: FeasibilityLevel,
        feasibility_probability: float
    ) -> str:
        """Generate detailed reasoning for feasibility assessment."""
        reasoning_parts = []
        
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("INTERCEPTION FEASIBILITY ASSESSMENT")
        reasoning_parts.append("MATHEMATICAL ANALYSIS ONLY")
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("")
        reasoning_parts.append("IMPORTANT: This is a MATHEMATICAL FEASIBILITY ASSESSMENT ONLY.")
        reasoning_parts.append("It does NOT provide:")
        reasoning_parts.append("  - Missile or interceptor modeling")
        reasoning_parts.append("  - Control laws")
        reasoning_parts.append("  - Execution timelines")
        reasoning_parts.append("  - Optimal intercept vectors")
        reasoning_parts.append("  - Action recommendations")
        reasoning_parts.append("")
        
        reasoning_parts.append(f"Feasibility Level: {feasibility_level.value}")
        reasoning_parts.append(f"Feasibility Probability: {feasibility_probability:.2%}")
        reasoning_parts.append("")
        
        reasoning_parts.append("Geometry Analysis:")
        reasoning_parts.append(f"  - Current Range: {geometry.geometry_parameters['range_meters']/1000.0:.2f} km")
        reasoning_parts.append(f"  - Relative Speed: {geometry.relative_speed:.1f} m/s")
        reasoning_parts.append(f"  - Closing Velocity: {geometry.closing_velocity:.1f} m/s")
        reasoning_parts.append(f"  - Bearing: {geometry.bearing_angle_degrees:.1f}°")
        reasoning_parts.append(f"  - Elevation: {geometry.elevation_angle_degrees:.1f}°")
        reasoning_parts.append("")
        
        reasoning_parts.append("Closest Approach:")
        reasoning_parts.append(f"  - Time to Closest Approach: {closest_approach.time_to_closest_approach_seconds:.1f} seconds")
        reasoning_parts.append(f"  - Closest Approach Distance: {closest_approach.closest_approach_distance_meters/1000.0:.2f} km")
        reasoning_parts.append(f"  - Confidence: {closest_approach.confidence:.2%}")
        reasoning_parts.append(f"  - Uncertainty: {closest_approach.uncertainty:.2%}")
        reasoning_parts.append("")
        
        reasoning_parts.append("=" * 60)
        reasoning_parts.append("END OF MATHEMATICAL FEASIBILITY ASSESSMENT")
        reasoning_parts.append("=" * 60)
        
        return "\n".join(reasoning_parts)

