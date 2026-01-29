"""
Threat assessment and classification engine.

Analyzes tracks to determine threat levels and classify entity types.
All assessments are probabilistic and advisory only.

FAIL-SAFE DECLARATIONS:
- Default advisory state: MONITORING_ONLY
- Fail-safe state: NO_ACTION
- If confidence is insufficient, the assessment defaults to NO_ACTION / MONITORING_ONLY
"""

import math
from typing import Dict, Optional
from enum import Enum

from abhedya.core.interfaces import IThreatAssessor
from abhedya.core.models import (
    Track,
    EntityType,
    ThreatLevel,
    SensorType
)
from abhedya.core.constants import (
    THREAT_LEVEL_NONE_THRESHOLD,
    THREAT_LEVEL_LOW_THRESHOLD,
    THREAT_LEVEL_MEDIUM_THRESHOLD,
    THREAT_LEVEL_HIGH_THRESHOLD,
    THREAT_LEVEL_CRITICAL_THRESHOLD
)


class AdvisoryState(str, Enum):
    """
    Advisory state declarations (INFORMATIONAL ONLY).
    
    These are declarations of default and fail-safe states.
    They do NOT execute any actions or connect to decision execution.
    """
    DEFAULT_ADVISORY_STATE = "MONITORING_ONLY"
    FAIL_SAFE_STATE = "NO_ACTION"


class FailSafeDeclarations:
    """
    Fail-safe state declarations for threat assessment.
    
    These are informational declarations only - they do NOT execute
    any actions or connect to decision execution logic.
    """
    DEFAULT_ADVISORY_STATE: str = AdvisoryState.DEFAULT_ADVISORY_STATE.value
    FAIL_SAFE_STATE: str = AdvisoryState.FAIL_SAFE_STATE.value
    
    # Fail-safe condition: If confidence is insufficient,
    # the assessment defaults to NO_ACTION / MONITORING_ONLY
    FAIL_SAFE_ON_INSUFFICIENT_CONFIDENCE: bool = True


class ThreatAssessor(IThreatAssessor):
    """
    Threat assessment engine.
    
    Analyzes tracks using deterministic rules and probabilistic
    reasoning to assess threat levels and classify entities.
    
    FAIL-SAFE BEHAVIOR:
    If confidence is insufficient, the assessment defaults to 
    NO_ACTION / MONITORING_ONLY. This is an informational declaration
    only - no actions are executed by this module.
    
    Default advisory state: MONITORING_ONLY
    Fail-safe state: NO_ACTION
    """
    
    def __init__(
        self,
        protected_zone_radius: float = 50000.0,  # 50 km
        critical_zone_radius: float = 20000.0,  # 20 km
        hostile_speed_threshold: float = 300.0  # m/s (typical fighter speed)
    ):
        """
        Initialize threat assessor.
        
        Args:
            protected_zone_radius: Radius of protected zone (meters)
            critical_zone_radius: Radius of critical zone (meters)
            hostile_speed_threshold: Speed threshold for hostile classification (m/s)
        """
        self.protected_zone_radius = protected_zone_radius
        self.critical_zone_radius = critical_zone_radius
        self.hostile_speed_threshold = hostile_speed_threshold
    
    def assess_track(self, track: Track) -> Track:
        """
        Assess threat level and classify entity type for a track.
        
        FAIL-SAFE: If confidence is insufficient, the assessment 
        defaults to NO_ACTION / MONITORING_ONLY. This is an 
        informational declaration only - no actions are executed.
        
        Args:
            track: Track to assess
            
        Returns:
            Updated track with threat assessment
        """
        # Classify entity type first
        entity_type = self._classify_entity(track)
        track.entity_type = entity_type
        
        # Assess threat level
        threat_level = self._assess_threat_level(track)
        track.threat_level = threat_level
        
        return track
    
    def _classify_entity(self, track: Track) -> EntityType:
        """
        Classify entity type based on sensor data and behavior.
        
        Returns:
            Classified entity type
        """
        # Check IFF data first (most reliable)
        iff_data = self._get_iff_data(track)
        if iff_data:
            if iff_data.get("is_friendly"):
                return EntityType.FRIENDLY
            elif iff_data.get("iff_response") == "NO_RESPONSE":
                # No IFF response could indicate hostile or civilian
                # Need additional analysis
                pass
        
        # Analyze behavior patterns
        behavior_score = self._analyze_behavior(track)
        
        # Analyze speed
        speed = track.velocity.speed if track.velocity else 0.0
        
        # Classification logic
        if iff_data and iff_data.get("is_friendly"):
            return EntityType.FRIENDLY
        elif speed > self.hostile_speed_threshold and behavior_score > 0.7:
            return EntityType.HOSTILE
        elif speed < 100.0:  # Slow moving, likely civilian
            return EntityType.CIVILIAN
        elif behavior_score < 0.3:
            return EntityType.NEUTRAL
        else:
            return EntityType.UNKNOWN
    
    def _get_iff_data(self, track: Track) -> Optional[Dict]:
        """Extract IFF data from sensor readings."""
        for reading in track.sensor_readings:
            if reading.sensor_type == SensorType.IFF:
                return reading.metadata
        return None
    
    def _analyze_behavior(self, track: Track) -> float:
        """
        Analyze track behavior patterns.
        
        Returns:
            Behavior score (0-1), higher indicates more hostile-like behavior
        """
        if not track.velocity:
            return 0.0
        
        score = 0.0
        
        # Speed analysis
        speed = track.velocity.speed
        if speed > self.hostile_speed_threshold:
            score += 0.3
        elif speed > 200.0:
            score += 0.15
        
        # Proximity to protected zone
        distance = self._calculate_distance_to_origin(track.position)
        if distance < self.critical_zone_radius:
            score += 0.4
        elif distance < self.protected_zone_radius:
            score += 0.2
        
        # Trajectory analysis (simplified)
        if len(track.sensor_readings) > 1:
            trajectory_score = self._analyze_trajectory(track)
            score += trajectory_score * 0.3
        
        return min(1.0, score)
    
    def _analyze_trajectory(self, track: Track) -> float:
        """
        Analyze trajectory patterns.
        
        Returns:
            Trajectory score (0-1)
        """
        if len(track.sensor_readings) < 2:
            return 0.0
        
        # Check if heading towards origin (protected zone)
        if track.velocity:
            heading_to_origin = self._calculate_heading_to_origin(
                track.position,
                track.velocity
            )
            
            # If heading directly towards origin, higher threat
            if abs(heading_to_origin) < 30.0:  # Within 30 degrees
                return 0.8
            elif abs(heading_to_origin) < 60.0:
                return 0.5
        
        return 0.2
    
    def _calculate_distance_to_origin(self, position) -> float:
        """Calculate distance from position to system origin."""
        return math.sqrt(position.x**2 + position.y**2 + position.z**2)
    
    def _calculate_heading_to_origin(self, position, velocity) -> float:
        """
        Calculate angle between velocity vector and vector to origin.
        
        Returns:
            Angle in degrees (0 = heading directly towards origin)
        """
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
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to valid range
        
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    def _assess_threat_level(self, track: Track) -> ThreatLevel:
        """
        Assess threat level based on entity type, position, and behavior.
        
        FAIL-SAFE: If confidence is insufficient, the assessment 
        defaults to NO_ACTION / MONITORING_ONLY. This is an 
        informational declaration only - no actions are executed.
        
        Returns:
            Assessed threat level (INFORMATIONAL ONLY - does not map to actions)
        """
        # Base threat score
        threat_score = 0.0
        
        # Entity type contribution
        if track.entity_type == EntityType.HOSTILE:
            threat_score += 0.6
        elif track.entity_type == EntityType.UNKNOWN:
            threat_score += 0.3
        elif track.entity_type == EntityType.FRIENDLY:
            threat_score += 0.0
        elif track.entity_type == EntityType.CIVILIAN:
            threat_score += 0.1
        else:  # NEUTRAL
            threat_score += 0.2
        
        # Proximity contribution
        distance = self._calculate_distance_to_origin(track.position)
        if distance < self.critical_zone_radius:
            proximity_factor = 0.4
        elif distance < self.protected_zone_radius:
            proximity_factor = 0.2
        else:
            proximity_factor = 0.0
        
        threat_score += proximity_factor
        
        # Behavior contribution
        behavior_score = self._analyze_behavior(track)
        threat_score += behavior_score * 0.2
        
        # Clamp to [0, 1]
        threat_score = max(0.0, min(1.0, threat_score))
        
        # FAIL-SAFE: Check confidence threshold
        # If confidence is insufficient, default to NONE threat level
        # This corresponds to NO_ACTION / MONITORING_ONLY state
        # (Informational declaration only - no actions executed)
        from abhedya.infrastructure.config.config import ConfidenceThresholds
        if track.confidence < ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE:
            # Insufficient confidence - default to NONE (NO_ACTION / MONITORING_ONLY)
            return ThreatLevel.NONE
        
        # Map to threat level (INFORMATIONAL ONLY - does not map to actions)
        if threat_score >= THREAT_LEVEL_CRITICAL_THRESHOLD:
            return ThreatLevel.CRITICAL
        elif threat_score >= THREAT_LEVEL_HIGH_THRESHOLD:
            return ThreatLevel.HIGH
        elif threat_score >= THREAT_LEVEL_MEDIUM_THRESHOLD:
            return ThreatLevel.MEDIUM
        elif threat_score >= THREAT_LEVEL_LOW_THRESHOLD:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.NONE
    
    def explain_assessment(self, track: Track) -> str:
        """
        Provide human-readable explanation of threat assessment.
        
        FAIL-SAFE: If confidence is insufficient, the assessment 
        defaults to NO_ACTION / MONITORING_ONLY. This is an 
        informational declaration only - no actions are executed.
        
        Args:
            track: Track to explain
            
        Returns:
            Explanation string
        """
        explanation_parts = []
        
        # Entity classification explanation
        explanation_parts.append(
            f"Entity Type: {track.entity_type.value}"
        )
        
        # IFF status
        iff_data = self._get_iff_data(track)
        if iff_data:
            if iff_data.get("is_friendly"):
                explanation_parts.append("IFF Status: FRIENDLY (Valid IFF response)")
            elif iff_data.get("iff_response") == "NO_RESPONSE":
                explanation_parts.append("IFF Status: NO RESPONSE")
            else:
                explanation_parts.append(f"IFF Status: {iff_data.get('iff_response')}")
        else:
            explanation_parts.append("IFF Status: No IFF data available")
        
        # Position and distance
        distance = self._calculate_distance_to_origin(track.position)
        explanation_parts.append(
            f"Distance from origin: {distance/1000.0:.2f} km"
        )
        
        if distance < self.critical_zone_radius:
            explanation_parts.append("Status: WITHIN CRITICAL ZONE")
        elif distance < self.protected_zone_radius:
            explanation_parts.append("Status: WITHIN PROTECTED ZONE")
        else:
            explanation_parts.append("Status: OUTSIDE PROTECTED ZONE")
        
        # Speed
        if track.velocity:
            speed = track.velocity.speed
            explanation_parts.append(f"Speed: {speed:.1f} m/s ({speed*3.6:.1f} km/h)")
            
            if speed > self.hostile_speed_threshold:
                explanation_parts.append("Speed Analysis: High speed (potential hostile)")
        
        # Threat level
        explanation_parts.append(f"Threat Level: {track.threat_level.value}")
        
        # Confidence
        explanation_parts.append(f"Assessment Confidence: {track.confidence:.2%}")
        
        # Fail-safe declaration
        from abhedya.infrastructure.config.config import ConfidenceThresholds
        if track.confidence < ConfidenceThresholds.MINIMUM_THREAT_ASSESSMENT_CONFIDENCE:
            explanation_parts.append("")
            explanation_parts.append("FAIL-SAFE: Insufficient confidence detected.")
            explanation_parts.append(f"Default state: {FailSafeDeclarations.FAIL_SAFE_STATE} / {FailSafeDeclarations.DEFAULT_ADVISORY_STATE}")
            explanation_parts.append("(Informational declaration only - no actions executed)")
        
        return "\n".join(explanation_parts)

