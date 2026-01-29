"""
Risk Envelope Evaluation

Mathematical evaluation of risk envelopes.
No missile, interceptor, or guidance modeling.
"""

import math
from typing import Optional

from abhedya.interception_simulation.models import RiskEnvelopeResult
from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.interception_simulation.geometry import GeometryAnalyzer


class RiskEnvelopeEvaluator:
    """
    Evaluates risk envelopes using mathematical analysis only.
    
    No missile, interceptor, or guidance modeling.
    """
    
    def __init__(self):
        """Initialize risk envelope evaluator."""
        self.geometry_analyzer = GeometryAnalyzer()
    
    def evaluate_envelope(
        self,
        defender_position: Coordinates,
        target_position: Coordinates,
        target_velocity: Velocity,
        envelope_radius_meters: float,
        defender_velocity: Optional[Velocity] = None
    ) -> RiskEnvelopeResult:
        """
        Evaluate risk envelope.
        
        Mathematical assessment only - no missile or interceptor modeling.
        
        Args:
            defender_position: Defender position
            target_position: Target position
            target_velocity: Target velocity
            envelope_radius_meters: Risk envelope radius
            defender_velocity: Defender velocity (default: stationary)
            
        Returns:
            RiskEnvelopeResult
        """
        if defender_velocity is None:
            defender_velocity = Velocity(vx=0.0, vy=0.0, vz=0.0)
        
        # Calculate current distance
        dx = target_position.x - defender_position.x
        dy = target_position.y - defender_position.y
        dz = target_position.z - defender_position.z
        current_distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        # Check if currently within envelope
        is_within_envelope = current_distance <= envelope_radius_meters
        
        # Analyze relative motion
        geometry = self.geometry_analyzer.analyze_relative_motion(
            defender_position,
            defender_velocity,
            target_position,
            target_velocity
        )
        
        # Calculate time to envelope penetration
        time_to_envelope = self._calculate_time_to_envelope(
            geometry.relative_position,
            geometry.relative_velocity,
            envelope_radius_meters
        )
        
        # Calculate penetration probability
        penetration_probability = self._calculate_penetration_probability(
            current_distance,
            envelope_radius_meters,
            geometry.closing_velocity,
            geometry.relative_speed
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(
            current_distance,
            envelope_radius_meters,
            penetration_probability
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            current_distance,
            envelope_radius_meters,
            geometry.relative_speed
        )
        
        return RiskEnvelopeResult(
            envelope_radius_meters=envelope_radius_meters,
            current_distance_meters=current_distance,
            is_within_envelope=is_within_envelope,
            time_to_envelope_seconds=time_to_envelope,
            envelope_penetration_probability=penetration_probability,
            risk_level=risk_level,
            confidence=confidence
        )
    
    def _calculate_time_to_envelope(
        self,
        relative_position: Coordinates,
        relative_velocity: Velocity,
        envelope_radius: float
    ) -> Optional[float]:
        """
        Calculate time to envelope penetration.
        
        Mathematical calculation only - no execution timelines.
        
        Args:
            relative_position: Relative position
            relative_velocity: Relative velocity
            envelope_radius: Envelope radius
            
        Returns:
            Time to envelope in seconds, or None if not approaching
        """
        # Solve: |r + v*t| = envelope_radius
        # This is a quadratic equation: |r + v*t|² = R²
        # (r + v*t) · (r + v*t) = R²
        # r·r + 2*r·v*t + v·v*t² = R²
        
        r_dot_r = (
            relative_position.x**2 +
            relative_position.y**2 +
            relative_position.z**2
        )
        
        r_dot_v = (
            relative_position.x * relative_velocity.vx +
            relative_position.y * relative_velocity.vy +
            relative_position.z * relative_velocity.vz
        )
        
        v_dot_v = (
            relative_velocity.vx**2 +
            relative_velocity.vy**2 +
            relative_velocity.vz**2
        )
        
        if v_dot_v == 0:
            # No relative motion
            if r_dot_r <= envelope_radius**2:
                return 0.0  # Already within envelope
            else:
                return None  # Not approaching
        
        # Quadratic: a*t² + b*t + c = 0
        # where: a = v·v, b = 2*r·v, c = r·r - R²
        a = v_dot_v
        b = 2.0 * r_dot_v
        c = r_dot_r - envelope_radius**2
        
        # Discriminant
        discriminant = b**2 - 4.0 * a * c
        
        if discriminant < 0:
            # No real solutions - will not reach envelope
            return None
        
        # Calculate solutions
        sqrt_discriminant = math.sqrt(discriminant)
        t1 = (-b - sqrt_discriminant) / (2.0 * a)
        t2 = (-b + sqrt_discriminant) / (2.0 * a)
        
        # Return the earliest positive time
        if t1 > 0 and t2 > 0:
            return min(t1, t2)
        elif t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            # Both negative - already passed or will not reach
            return None
    
    def _calculate_penetration_probability(
        self,
        current_distance: float,
        envelope_radius: float,
        closing_velocity: float,
        relative_speed: float
    ) -> float:
        """
        Calculate probability of envelope penetration.
        
        Mathematical assessment only.
        
        Args:
            current_distance: Current distance
            envelope_radius: Envelope radius
            closing_velocity: Closing velocity
            relative_speed: Relative speed
            
        Returns:
            Penetration probability [0.0, 1.0]
        """
        # If already within envelope
        if current_distance <= envelope_radius:
            return 1.0
        
        # If not closing (departing)
        if closing_velocity <= 0:
            return 0.0
        
        # Distance to envelope boundary
        distance_to_boundary = current_distance - envelope_radius
        
        # Time to boundary at current closing velocity
        if closing_velocity > 0:
            time_to_boundary = distance_to_boundary / closing_velocity
        else:
            return 0.0
        
        # Probability based on time and relative speed
        # Shorter time and higher speed = higher probability
        if time_to_boundary < 60.0:  # Less than 1 minute
            time_factor = 0.9
        elif time_to_boundary < 300.0:  # Less than 5 minutes
            time_factor = 0.7
        elif time_to_boundary < 1800.0:  # Less than 30 minutes
            time_factor = 0.5
        else:
            time_factor = 0.3
        
        speed_factor = min(1.0, relative_speed / 500.0)  # Normalize to 500 m/s
        
        probability = time_factor * 0.7 + speed_factor * 0.3
        
        return max(0.0, min(1.0, probability))
    
    def _determine_risk_level(
        self,
        current_distance: float,
        envelope_radius: float,
        penetration_probability: float
    ) -> str:
        """Determine risk level."""
        if current_distance <= envelope_radius:
            return "WITHIN_ENVELOPE"
        elif penetration_probability > 0.8:
            return "HIGH_RISK"
        elif penetration_probability > 0.5:
            return "MEDIUM_RISK"
        elif penetration_probability > 0.2:
            return "LOW_RISK"
        else:
            return "MINIMAL_RISK"
    
    def _calculate_confidence(
        self,
        current_distance: float,
        envelope_radius: float,
        relative_speed: float
    ) -> float:
        """Calculate confidence in risk envelope assessment."""
        # Confidence decreases with distance
        distance_factor = 1.0 - min(1.0, current_distance / 200000.0)  # 200 km max
        
        # Confidence decreases with speed (higher speed = less certain)
        speed_factor = 1.0 - min(1.0, relative_speed / 1000.0)
        
        # Higher confidence if close to envelope boundary
        if abs(current_distance - envelope_radius) < envelope_radius * 0.1:
            proximity_factor = 0.9
        else:
            proximity_factor = 0.5
        
        confidence = (distance_factor * 0.4 + speed_factor * 0.3 + proximity_factor * 0.3)
        
        return max(0.0, min(1.0, confidence))

