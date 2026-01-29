"""
Probabilistic Classification Module

Classical statistical techniques for classifying objects into:
- Aerial Drone
- Aircraft
- Unknown Object

All classifications include uncertainty and reasoning.
"""

import math
from typing import Dict, Any, Optional
from dataclasses import dataclass

from abhedya.tracking.models import ObjectType, ClassificationResult
from abhedya.domain.value_objects import Velocity
from abhedya.infrastructure.config.config import ThreatAssessmentThresholds


@dataclass
class ClassificationFeatures:
    """Features used for classification."""
    speed_meters_per_second: float
    altitude_meters: float
    radar_cross_section: float
    maneuverability_score: float  # 0.0 to 1.0
    size_category: str  # "SMALL", "MEDIUM", "LARGE"


class ProbabilisticClassifier:
    """
    Probabilistic classifier using classical statistical techniques.
    
    Classifies objects into:
    - Aerial Drone: Small, low altitude, low speed, high maneuverability
    - Aircraft: Medium to large, high altitude, high speed, low maneuverability
    - Unknown Object: Does not match known patterns
    
    All classifications include uncertainty and reasoning.
    """
    
    def __init__(
        self,
        unknown_threshold: float = 0.4  # Minimum probability to classify as known type
    ):
        """
        Initialize classifier.
        
        Args:
            unknown_threshold: Minimum probability to classify as known type
                              (below this, classify as UNKNOWN_OBJECT)
        """
        self.unknown_threshold = unknown_threshold
    
    def classify(
        self,
        detection: Dict[str, Any],
        historical_detections: Optional[list] = None
    ) -> ClassificationResult:
        """
        Classify object from detection data.
        
        Args:
            detection: Detection dictionary
            historical_detections: Historical detections for context (optional)
            
        Returns:
            ClassificationResult with probabilities and uncertainty
        """
        # Extract features
        features = self._extract_features(detection, historical_detections)
        
        # Calculate probabilities for each type
        probabilities = {
            ObjectType.AERIAL_DRONE: self._calculate_drone_probability(features),
            ObjectType.AIRCRAFT: self._calculate_aircraft_probability(features),
            ObjectType.UNKNOWN_OBJECT: self._calculate_unknown_probability(features)
        }
        
        # Normalize probabilities to sum to 1.0
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v / total for k, v in probabilities.items()}
        else:
            # If all probabilities are zero, default to unknown
            probabilities = {
                ObjectType.AERIAL_DRONE: 0.0,
                ObjectType.AIRCRAFT: 0.0,
                ObjectType.UNKNOWN_OBJECT: 1.0
            }
        
        # Determine classification
        max_prob_type = max(probabilities.items(), key=lambda x: x[1])[0]
        max_prob = probabilities[max_prob_type]
        
        # If maximum probability is below threshold, classify as unknown
        if max_prob < self.unknown_threshold:
            object_type = ObjectType.UNKNOWN_OBJECT
            probability = probabilities[ObjectType.UNKNOWN_OBJECT]
        else:
            object_type = max_prob_type
            probability = max_prob
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(probabilities)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(features, probabilities, object_type)
        
        return ClassificationResult(
            object_type=object_type,
            probability=probability,
            uncertainty=uncertainty,
            probabilities=probabilities,
            reasoning=reasoning
        )
    
    def _extract_features(
        self,
        detection: Dict[str, Any],
        historical_detections: Optional[list] = None
    ) -> ClassificationFeatures:
        """Extract classification features from detection."""
        # Speed
        velocity = detection.get("velocity", {})
        vx = velocity.get("vx", 0.0)
        vy = velocity.get("vy", 0.0)
        vz = velocity.get("vz", 0.0)
        speed = math.sqrt(vx**2 + vy**2 + vz**2)
        
        # Altitude
        position = detection.get("position", {})
        altitude = position.get("z", 0.0)
        
        # Radar cross section
        metadata = detection.get("metadata", {})
        rcs = metadata.get("radar_cross_section", 0.5)
        
        # Size category
        size_category = metadata.get("size_category", "MEDIUM")
        
        # Maneuverability (calculate from velocity changes if historical data available)
        maneuverability = 0.5  # Default
        if historical_detections and len(historical_detections) > 1:
            maneuverability = self._calculate_maneuverability(
                detection,
                historical_detections
            )
        
        return ClassificationFeatures(
            speed_meters_per_second=speed,
            altitude_meters=altitude,
            radar_cross_section=rcs,
            maneuverability_score=maneuverability,
            size_category=size_category
        )
    
    def _calculate_maneuverability(
        self,
        detection: Dict[str, Any],
        historical_detections: list
    ) -> float:
        """
        Calculate maneuverability score from velocity changes.
        
        Args:
            detection: Current detection
            historical_detections: Historical detections
            
        Returns:
            Maneuverability score [0.0, 1.0]
        """
        if len(historical_detections) < 2:
            return 0.5
        
        # Get current and previous velocities
        current_vel = detection.get("velocity", {})
        prev_vel = historical_detections[-1].get("velocity", {})
        
        current_speed = math.sqrt(
            current_vel.get("vx", 0.0)**2 +
            current_vel.get("vy", 0.0)**2 +
            current_vel.get("vz", 0.0)**2
        )
        prev_speed = math.sqrt(
            prev_vel.get("vx", 0.0)**2 +
            prev_vel.get("vy", 0.0)**2 +
            prev_vel.get("vz", 0.0)**2
        )
        
        # Calculate speed change rate
        speed_change = abs(current_speed - prev_speed)
        
        # Calculate direction change
        if current_speed > 0 and prev_speed > 0:
            # Calculate angle between velocity vectors
            dot_product = (
                current_vel.get("vx", 0.0) * prev_vel.get("vx", 0.0) +
                current_vel.get("vy", 0.0) * prev_vel.get("vy", 0.0) +
                current_vel.get("vz", 0.0) * prev_vel.get("vz", 0.0)
            )
            cos_angle = dot_product / (current_speed * prev_speed)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle_change = math.acos(cos_angle)
        else:
            angle_change = 0.0
        
        # Maneuverability increases with speed changes and direction changes
        maneuverability = min(1.0, (speed_change / 50.0) + (angle_change / math.pi))
        
        return maneuverability
    
    def _calculate_drone_probability(self, features: ClassificationFeatures) -> float:
        """
        Calculate probability that object is an aerial drone.
        
        Drone characteristics:
        - Small size
        - Low altitude (< 1 km)
        - Low to medium speed (20-100 m/s)
        - High maneuverability
        - Small RCS
        """
        probability = 0.0
        
        # Size factor
        if features.size_category == "SMALL":
            probability += 0.3
        elif features.size_category == "MEDIUM":
            probability += 0.1
        
        # Altitude factor (drones typically low altitude)
        if features.altitude_meters < 1000.0:
            altitude_factor = 1.0 - (features.altitude_meters / 1000.0)
            probability += 0.3 * altitude_factor
        elif features.altitude_meters < 2000.0:
            altitude_factor = 1.0 - ((features.altitude_meters - 1000.0) / 1000.0)
            probability += 0.1 * altitude_factor
        
        # Speed factor (drones typically 20-100 m/s)
        if 20.0 <= features.speed_meters_per_second <= 100.0:
            speed_factor = 1.0 - abs(features.speed_meters_per_second - 60.0) / 40.0
            probability += 0.2 * max(0.0, speed_factor)
        elif features.speed_meters_per_second < 20.0:
            probability += 0.1
        
        # Maneuverability factor (drones are highly maneuverable)
        probability += 0.2 * features.maneuverability_score
        
        # RCS factor (drones have small RCS)
        if features.radar_cross_section < 0.3:
            probability += 0.1
        
        return min(1.0, probability)
    
    def _calculate_aircraft_probability(self, features: ClassificationFeatures) -> float:
        """
        Calculate probability that object is an aircraft.
        
        Aircraft characteristics:
        - Medium to large size
        - High altitude (> 5 km typically)
        - High speed (200-400 m/s)
        - Low maneuverability
        - Medium to large RCS
        """
        probability = 0.0
        
        # Size factor
        if features.size_category == "LARGE":
            probability += 0.3
        elif features.size_category == "MEDIUM":
            probability += 0.2
        
        # Altitude factor (aircraft typically high altitude)
        if features.altitude_meters > 5000.0:
            altitude_factor = min(1.0, (features.altitude_meters - 5000.0) / 10000.0)
            probability += 0.3 * altitude_factor
        elif features.altitude_meters > 2000.0:
            altitude_factor = (features.altitude_meters - 2000.0) / 3000.0
            probability += 0.1 * altitude_factor
        
        # Speed factor (aircraft typically 200-400 m/s)
        if 200.0 <= features.speed_meters_per_second <= 400.0:
            speed_factor = 1.0 - abs(features.speed_meters_per_second - 300.0) / 100.0
            probability += 0.3 * max(0.0, speed_factor)
        elif features.speed_meters_per_second > 400.0:
            probability += 0.1
        
        # Maneuverability factor (aircraft have low maneuverability)
        probability += 0.1 * (1.0 - features.maneuverability_score)
        
        # RCS factor (aircraft have medium to large RCS)
        if features.radar_cross_section > 0.5:
            probability += 0.1
        
        return min(1.0, probability)
    
    def _calculate_unknown_probability(self, features: ClassificationFeatures) -> float:
        """
        Calculate probability that object is unknown.
        
        Unknown objects are those that don't match known patterns well.
        """
        # Calculate how well features match known types
        drone_prob = self._calculate_drone_probability(features)
        aircraft_prob = self._calculate_aircraft_probability(features)
        
        # Unknown probability is inverse of best match
        max_known_prob = max(drone_prob, aircraft_prob)
        unknown_prob = 1.0 - max_known_prob
        
        # Boost unknown probability if features are ambiguous
        if abs(drone_prob - aircraft_prob) < 0.2:
            unknown_prob += 0.2
        
        return min(1.0, unknown_prob)
    
    def _calculate_uncertainty(
        self,
        probabilities: Dict[ObjectType, float]
    ) -> float:
        """
        Calculate classification uncertainty.
        
        Uncertainty is high when probabilities are similar (ambiguous).
        Uncertainty is low when one probability is much higher than others.
        
        Uses entropy-based measure: H = -Σ(p * log2(p))
        """
        # Calculate entropy
        entropy = 0.0
        for prob in probabilities.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        # Normalize to [0, 1] (max entropy for 3 classes is log2(3) ≈ 1.585)
        max_entropy = math.log2(len(probabilities))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return normalized_entropy
    
    def _generate_reasoning(
        self,
        features: ClassificationFeatures,
        probabilities: Dict[ObjectType, float],
        object_type: ObjectType
    ) -> str:
        """Generate human-readable reasoning for classification."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Classification: {object_type.value}")
        reasoning_parts.append(f"Probability: {probabilities[object_type]:.2%}")
        reasoning_parts.append(f"Uncertainty: {self._calculate_uncertainty(probabilities):.2%}")
        reasoning_parts.append("")
        reasoning_parts.append("Feature Analysis:")
        reasoning_parts.append(f"  - Speed: {features.speed_meters_per_second:.1f} m/s")
        reasoning_parts.append(f"  - Altitude: {features.altitude_meters:.1f} m")
        reasoning_parts.append(f"  - RCS: {features.radar_cross_section:.2f}")
        reasoning_parts.append(f"  - Size: {features.size_category}")
        reasoning_parts.append(f"  - Maneuverability: {features.maneuverability_score:.2f}")
        reasoning_parts.append("")
        reasoning_parts.append("Probabilities:")
        for obj_type, prob in probabilities.items():
            reasoning_parts.append(f"  - {obj_type.value}: {prob:.2%}")
        
        return "\n".join(reasoning_parts)

