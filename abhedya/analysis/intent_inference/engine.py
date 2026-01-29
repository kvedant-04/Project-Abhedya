"""
Intent Probability Inference Engine

Probabilistic intent assessment using explainable, rule-based logic.
All outputs are ADVISORY ONLY - no action recommendations.

CRITICAL CONSTRAINTS:
- NO deep learning models
- Explainable rule-based and statistical logic only
- Probabilities must sum to ≤ 100%
- Fail-safe to MONITORING_ONLY if inputs missing
"""

import uuid
import math
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from abhedya.analysis.intent_inference.models import (
    IntentProbabilityResult,
    IntentCategory
)
from abhedya.tracking.models import Track, ObjectType
from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.infrastructure.config.config import (
    ProtectedAirspaceConfiguration,
    ConfidenceThresholds
)


class IntentInferenceEngine:
    """
    Intent probability inference engine.
    
    STRICT RULES:
    - No binary decisions
    - No action recommendations
    - Intent probabilities do NOT map to any actions
    - Output must explicitly state: "Advisory Assessment Only"
    - Explainable rule-based logic only (NO deep learning)
    
    Provides:
    - Probabilistic intent estimates (Transit, Surveillance, Hostile)
    - Overall intent confidence
    - Human-readable reasoning
    - Uncertainty-aware and conservative by default
    """
    
    def __init__(self):
        """Initialize intent inference engine."""
        # Intent inference thresholds (meters, m/s, etc.)
        self.LOITERING_RADIUS_METERS = 5000.0  # 5 km radius for loitering
        self.LOITERING_TIME_SECONDS = 300.0  # 5 minutes for sustained loitering
        self.SURVEILLANCE_ALTITUDE_VARIANCE_METERS = 100.0  # Low altitude variance
        self.PROBING_DISTANCE_METERS = 10000.0  # 10 km for perimeter probing
        self.TRANSIT_SPEED_MIN_METERS_PER_SECOND = 50.0  # ~180 km/h minimum
        self.TRANSIT_SPEED_MAX_METERS_PER_SECOND = 300.0  # ~1080 km/h maximum
        self.MANEUVER_STABILITY_THRESHOLD = 0.1  # Velocity change threshold
    
    def infer_intent(
        self,
        track: Track,
        trajectory_prediction: Optional[Any] = None,
        proximity_estimate: Optional[Any] = None,
        additional_context: Optional[Dict[str, Any]] = None,
        is_training_mode: bool = False
    ) -> Optional[IntentProbabilityResult]:
        """
        Infer intent probabilities for a track.
        
        IMPORTANT: This is an ADVISORY ASSESSMENT ONLY.
        It does NOT recommend any actions.
        Intent probabilities do NOT map to any actions.
        
        FAIL-SAFE: Returns None if required inputs are missing or inconsistent.
        System should default to MONITORING_ONLY in this case.
        
        Args:
            track: Track to assess
            trajectory_prediction: Optional trajectory prediction
            proximity_estimate: Optional proximity estimate
            additional_context: Optional additional context
            is_training_mode: Training mode flag
            
        Returns:
            IntentProbabilityResult or None if fail-safe triggered
        """
        # Fail-safe: Check required inputs
        if not track or not track.position:
            return None
        
        if not track.velocity:
            # Can still assess with position only, but lower confidence
            pass
        
        # Calculate intent indicators
        indicators = self._calculate_intent_indicators(
            track,
            trajectory_prediction,
            proximity_estimate,
            additional_context
        )
        
        # Calculate probabilities from indicators
        probabilities = self._calculate_probabilities(indicators, track)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(indicators, track)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(indicators, track)
        
        # Create result
        result = IntentProbabilityResult(
            assessment_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            track_id=track.identifier.track_id if track.identifier else None,
            transit_probability=probabilities[IntentCategory.TRANSIT],
            surveillance_probability=probabilities[IntentCategory.SURVEILLANCE],
            hostile_probability=probabilities[IntentCategory.HOSTILE],
            intent_confidence=confidence,
            reasoning=reasoning,
            metadata={
                "indicators": indicators,
                "object_type": track.classification.object_type.value if track.classification else None,
                "track_confidence": track.confidence
            },
            is_training_mode=is_training_mode
        )
        
        return result
    
    def _calculate_intent_indicators(
        self,
        track: Track,
        trajectory_prediction: Optional[Any],
        proximity_estimate: Optional[Any],
        additional_context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate intent indicators from track data.
        
        Returns dictionary of indicator values [0.0, 1.0].
        """
        indicators = {
            "loitering_score": 0.0,
            "transit_score": 0.0,
            "surveillance_score": 0.0,
            "hostile_score": 0.0,
            "maneuver_stability": 0.0,
            "proximity_risk": 0.0,
            "altitude_stability": 0.0,
            "speed_characteristics": 0.0
        }
        
        # Classification-based indicators
        if track.classification:
            object_type = track.classification.object_type
            if object_type == ObjectType.AERIAL_DRONE:
                # Drones more likely for surveillance
                indicators["surveillance_score"] += 0.2
            elif object_type == ObjectType.AIRCRAFT:
                # Aircraft more likely for transit
                indicators["transit_score"] += 0.2
            elif object_type == ObjectType.UNKNOWN_OBJECT:
                # Unknown objects have higher uncertainty
                indicators["surveillance_score"] += 0.1
                indicators["hostile_score"] += 0.1
        
        # Speed-based indicators
        if track.velocity:
            speed = track.velocity.speed
            
            # Transit: moderate to high speed, stable
            if self.TRANSIT_SPEED_MIN_METERS_PER_SECOND <= speed <= self.TRANSIT_SPEED_MAX_METERS_PER_SECOND:
                indicators["transit_score"] += 0.3
                indicators["speed_characteristics"] = 0.7
            
            # Loitering: low speed
            if speed < self.TRANSIT_SPEED_MIN_METERS_PER_SECOND:
                indicators["loitering_score"] += 0.3
                indicators["surveillance_score"] += 0.2
        
        # Position-based indicators (if history available)
        if additional_context and "position_history" in additional_context:
            position_history = additional_context["position_history"]
            if len(position_history) > 1:
                # Calculate loitering indicator
                loitering = self._calculate_loitering_indicator(position_history)
                indicators["loitering_score"] += loitering
                
                # Calculate maneuver stability
                if "velocity_history" in additional_context:
                    velocity_history = additional_context["velocity_history"]
                    stability = self._calculate_maneuver_stability(velocity_history)
                    indicators["maneuver_stability"] = stability
        
        # Trajectory-based indicators
        if trajectory_prediction and hasattr(trajectory_prediction, 'predicted_positions'):
            # Check if trajectory shows loitering pattern
            if len(trajectory_prediction.predicted_positions) > 5:
                trajectory_loitering = self._analyze_trajectory_loitering(
                    track.position,
                    trajectory_prediction.predicted_positions
                )
                indicators["loitering_score"] += trajectory_loitering * 0.3
        
        # Proximity-based indicators
        if proximity_estimate:
            if hasattr(proximity_estimate, 'is_approaching') and proximity_estimate.is_approaching:
                # Approaching protected zone
                if hasattr(proximity_estimate, 'current_distance_meters'):
                    distance = proximity_estimate.current_distance_meters
                    if distance < self.PROBING_DISTANCE_METERS:
                        indicators["proximity_risk"] = 0.6
                        indicators["surveillance_score"] += 0.2
                        indicators["hostile_score"] += 0.1
        
        # Normalize all indicators to [0.0, 1.0]
        for key in indicators:
            indicators[key] = max(0.0, min(1.0, indicators[key]))
        
        return indicators
    
    def _calculate_loitering_indicator(self, position_history: List[Coordinates]) -> float:
        """
        Calculate loitering indicator from position history.
        
        Returns value [0.0, 1.0] indicating loitering behavior.
        """
        if len(position_history) < 3:
            return 0.0
        
        # Calculate centroid
        centroid_x = sum(p.x for p in position_history) / len(position_history)
        centroid_y = sum(p.y for p in position_history) / len(position_history)
        centroid_z = sum(p.z for p in position_history) / len(position_history)
        
        # Calculate average distance from centroid
        distances = []
        for pos in position_history:
            dist = math.sqrt(
                (pos.x - centroid_x)**2 +
                (pos.y - centroid_y)**2 +
                (pos.z - centroid_z)**2
            )
            distances.append(dist)
        
        avg_distance = sum(distances) / len(distances)
        
        # Loitering if average distance is small
        if avg_distance < self.LOITERING_RADIUS_METERS:
            return 1.0 - (avg_distance / self.LOITERING_RADIUS_METERS)
        
        return 0.0
    
    def _calculate_maneuver_stability(self, velocity_history: List[Velocity]) -> float:
        """
        Calculate maneuver stability from velocity history.
        
        Returns value [0.0, 1.0] where 1.0 = very stable, 0.0 = unstable.
        """
        if len(velocity_history) < 2:
            return 0.5  # Neutral if insufficient data
        
        # Calculate velocity changes
        velocity_changes = []
        for i in range(1, len(velocity_history)):
            v1 = velocity_history[i-1]
            v2 = velocity_history[i]
            
            change = math.sqrt(
                (v2.vx - v1.vx)**2 +
                (v2.vy - v1.vy)**2 +
                (v2.vz - v1.vz)**2
            )
            velocity_changes.append(change)
        
        if not velocity_changes:
            return 0.5
        
        avg_change = sum(velocity_changes) / len(velocity_changes)
        
        # Stability: low change = high stability
        # Normalize based on typical velocity magnitude
        typical_speed = velocity_history[0].speed if velocity_history else 100.0
        stability = 1.0 - min(1.0, avg_change / (typical_speed * self.MANEUVER_STABILITY_THRESHOLD))
        
        return max(0.0, min(1.0, stability))
    
    def _analyze_trajectory_loitering(
        self,
        current_position: Coordinates,
        predicted_positions: List[Coordinates]
    ) -> float:
        """
        Analyze trajectory for loitering pattern.
        
        Returns value [0.0, 1.0] indicating loitering in predicted trajectory.
        """
        if len(predicted_positions) < 3:
            return 0.0
        
        # Calculate centroid of predicted positions
        centroid_x = sum(p.x for p in predicted_positions) / len(predicted_positions)
        centroid_y = sum(p.y for p in predicted_positions) / len(predicted_positions)
        centroid_z = sum(p.z for p in predicted_positions) / len(predicted_positions)
        
        # Calculate average distance from centroid
        distances = []
        for pos in predicted_positions:
            dist = math.sqrt(
                (pos.x - centroid_x)**2 +
                (pos.y - centroid_y)**2 +
                (pos.z - centroid_z)**2
            )
            distances.append(dist)
        
        avg_distance = sum(distances) / len(distances)
        
        # Loitering if average distance is small
        if avg_distance < self.LOITERING_RADIUS_METERS:
            return 1.0 - (avg_distance / self.LOITERING_RADIUS_METERS)
        
        return 0.0
    
    def _calculate_probabilities(
        self,
        indicators: Dict[str, float],
        track: Track
    ) -> Dict[IntentCategory, float]:
        """
        Calculate intent probabilities from indicators.
        
        Returns probabilities that sum to ≤ 1.0.
        """
        # Base probabilities
        transit_prob = 0.0
        surveillance_prob = 0.0
        hostile_prob = 0.0
        
        # Transit probability
        transit_prob += indicators["transit_score"] * 0.4
        transit_prob += indicators["speed_characteristics"] * 0.3
        transit_prob += (1.0 - indicators["loitering_score"]) * 0.2
        transit_prob += indicators["maneuver_stability"] * 0.1
        
        # Surveillance probability
        surveillance_prob += indicators["surveillance_score"] * 0.4
        surveillance_prob += indicators["loitering_score"] * 0.3
        surveillance_prob += indicators["altitude_stability"] * 0.2
        surveillance_prob += indicators["proximity_risk"] * 0.1
        
        # Hostile probability (conservative - requires strong indicators)
        hostile_prob += indicators["hostile_score"] * 0.5
        hostile_prob += indicators["proximity_risk"] * 0.3
        hostile_prob += (1.0 - indicators["maneuver_stability"]) * 0.2
        
        # Normalize to ensure sum ≤ 1.0
        total = transit_prob + surveillance_prob + hostile_prob
        if total > 1.0:
            scale = 1.0 / total
            transit_prob *= scale
            surveillance_prob *= scale
            hostile_prob *= scale
        
        # Ensure all probabilities are in [0.0, 1.0]
        transit_prob = max(0.0, min(1.0, transit_prob))
        surveillance_prob = max(0.0, min(1.0, surveillance_prob))
        hostile_prob = max(0.0, min(1.0, hostile_prob))
        
        return {
            IntentCategory.TRANSIT: transit_prob,
            IntentCategory.SURVEILLANCE: surveillance_prob,
            IntentCategory.HOSTILE: hostile_prob
        }
    
    def _calculate_confidence(
        self,
        indicators: Dict[str, float],
        track: Track
    ) -> float:
        """
        Calculate overall confidence in intent assessment.
        
        Returns confidence [0.0, 1.0].
        """
        # Base confidence from track confidence
        confidence = track.confidence if track.confidence else 0.5
        
        # Adjust based on data quality
        if track.velocity:
            confidence += 0.1
        
        if track.classification and track.classification.probability > 0.7:
            confidence += 0.1
        
        # Reduce confidence if data is sparse
        if indicators["maneuver_stability"] == 0.0:
            confidence *= 0.8
        
        # Ensure confidence is in [0.0, 1.0]
        return max(0.0, min(1.0, confidence))
    
    def _generate_reasoning(
        self,
        indicators: Dict[str, float],
        track: Track
    ) -> List[str]:
        """
        Generate human-readable reasoning for intent assessment.
        
        Returns list of reasoning statements.
        """
        reasoning = []
        
        # Classification reasoning
        if track.classification:
            object_type = track.classification.object_type.value
            reasoning.append(f"Object classified as: {object_type}")
        
        # Speed reasoning
        if track.velocity:
            speed_kmh = track.velocity.speed * 3.6  # Convert m/s to km/h
            reasoning.append(f"Current speed: {speed_kmh:.1f} km/h")
        
        # Loitering reasoning
        if indicators["loitering_score"] > 0.5:
            reasoning.append("Sustained loitering pattern detected")
        
        # Transit reasoning
        if indicators["transit_score"] > 0.5:
            reasoning.append("Transit-like speed and trajectory characteristics")
        
        # Surveillance reasoning
        if indicators["surveillance_score"] > 0.5:
            reasoning.append("Surveillance-like behavior patterns observed")
        
        # Proximity reasoning
        if indicators["proximity_risk"] > 0.5:
            reasoning.append("Approaching or near protected airspace boundary")
        
        # Maneuver stability reasoning
        if indicators["maneuver_stability"] > 0.7:
            reasoning.append("Stable maneuver patterns observed")
        elif indicators["maneuver_stability"] < 0.3:
            reasoning.append("Variable maneuver patterns observed")
        
        # Default reasoning if none generated
        if not reasoning:
            reasoning.append("Insufficient data for detailed intent assessment")
        
        return reasoning

