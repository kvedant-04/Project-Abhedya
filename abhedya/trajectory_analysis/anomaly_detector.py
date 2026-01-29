"""
Anomaly Detection Module

Detects physically implausible or anomalous motion.
Anomalies do NOT imply hostile intent - they indicate unusual motion patterns.

Uses classical statistical techniques and physics validation.
"""

import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from abhedya.trajectory_analysis.models import (
    AnomalyDetectionResult,
    AnomalyType
)
from abhedya.trajectory_analysis.physics_validator import PhysicsValidator
from abhedya.domain.value_objects import Coordinates, Velocity


class AnomalyDetector:
    """
    Detects anomalous motion patterns.
    
    IMPORTANT: Anomalies do NOT imply hostile intent.
    They indicate unusual motion that may require investigation.
    
    Detects:
    - Sudden direction changes
    - Sudden speed changes
    - Unusual acceleration patterns
    - Unusual trajectory patterns
    - Physics violations
    """
    
    def __init__(
        self,
        sudden_direction_change_threshold_degrees: float = 45.0,
        sudden_speed_change_threshold_percent: float = 0.5,  # 50% change
        unusual_acceleration_threshold: float = 50.0  # m/s²
    ):
        """
        Initialize anomaly detector.
        
        Args:
            sudden_direction_change_threshold_degrees: Threshold for sudden direction change
            sudden_speed_change_threshold_percent: Threshold for sudden speed change (0-1)
            unusual_acceleration_threshold: Threshold for unusual acceleration (m/s²)
        """
        self.direction_change_threshold = math.radians(sudden_direction_change_threshold_degrees)
        self.speed_change_threshold = sudden_speed_change_threshold_percent
        self.acceleration_threshold = unusual_acceleration_threshold
        self.physics_validator = PhysicsValidator()
    
    def detect_anomalies(
        self,
        positions: List[Coordinates],
        velocities: List[Velocity],
        timestamps: Optional[List[float]] = None
    ) -> AnomalyDetectionResult:
        """
        Detect anomalies in motion sequence.
        
        Args:
            positions: List of positions
            velocities: List of velocities
            timestamps: List of timestamps in seconds (optional)
            
        Returns:
            AnomalyDetectionResult
        """
        anomalies = []
        anomaly_score = 0.0
        
        if len(positions) < 3 or len(velocities) < 3:
            return AnomalyDetectionResult(
                is_anomalous=False,
                anomaly_types=[],
                anomaly_score=0.0,
                reasoning="Insufficient data for anomaly detection",
                note="Anomalies do NOT imply hostile intent"
            )
        
        # Use provided timestamps or assume 1s intervals
        if timestamps is None:
            timestamps = [float(i) for i in range(len(positions))]
        
        # Check for physics violations
        physics_result = self.physics_validator.validate_motion(
            positions, velocities, timestamps
        )
        if not physics_result.is_valid:
            anomalies.append(AnomalyType.PHYSICS_VIOLATION)
            anomaly_score += 0.5
        
        # Check for sudden direction changes
        direction_anomalies = self._detect_direction_changes(velocities, timestamps)
        anomalies.extend(direction_anomalies)
        if direction_anomalies:
            anomaly_score += 0.3
        
        # Check for sudden speed changes
        speed_anomalies = self._detect_speed_changes(velocities, timestamps)
        anomalies.extend(speed_anomalies)
        if speed_anomalies:
            anomaly_score += 0.2
        
        # Check for unusual acceleration
        accel_anomalies = self._detect_unusual_acceleration(velocities, timestamps)
        anomalies.extend(accel_anomalies)
        if accel_anomalies:
            anomaly_score += 0.2
        
        # Check for unusual trajectory
        trajectory_anomalies = self._detect_unusual_trajectory(positions, timestamps)
        anomalies.extend(trajectory_anomalies)
        if trajectory_anomalies:
            anomaly_score += 0.1
        
        # Normalize anomaly score
        anomaly_score = min(1.0, anomaly_score)
        
        # Determine if anomalous
        is_anomalous = len(anomalies) > 0 or anomaly_score > 0.3
        
        # Generate reasoning
        reasoning = self._generate_reasoning(anomalies, anomaly_score)
        
        return AnomalyDetectionResult(
            is_anomalous=is_anomalous,
            anomaly_types=list(set(anomalies)),  # Remove duplicates
            anomaly_score=anomaly_score,
            reasoning=reasoning,
            note="IMPORTANT: Anomalies do NOT imply hostile intent. They indicate unusual motion patterns that may require investigation."
        )
    
    def _detect_direction_changes(
        self,
        velocities: List[Velocity],
        timestamps: List[float]
    ) -> List[AnomalyType]:
        """Detect sudden direction changes."""
        anomalies = []
        
        for i in range(1, len(velocities)):
            prev_vel = velocities[i-1]
            curr_vel = velocities[i]
            
            prev_speed = prev_vel.speed
            curr_speed = curr_vel.speed
            
            if prev_speed == 0 or curr_speed == 0:
                continue
            
            # Calculate angle between velocity vectors
            dot_product = (
                prev_vel.vx * curr_vel.vx +
                prev_vel.vy * curr_vel.vy +
                prev_vel.vz * curr_vel.vz
            )
            cos_angle = dot_product / (prev_speed * curr_speed)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle = math.acos(cos_angle)
            
            # Check if angle change exceeds threshold
            if angle > self.direction_change_threshold:
                anomalies.append(AnomalyType.SUDDEN_DIRECTION_CHANGE)
        
        return anomalies
    
    def _detect_speed_changes(
        self,
        velocities: List[Velocity],
        timestamps: List[float]
    ) -> List[AnomalyType]:
        """Detect sudden speed changes."""
        anomalies = []
        
        for i in range(1, len(velocities)):
            prev_vel = velocities[i-1]
            curr_vel = velocities[i]
            
            prev_speed = prev_vel.speed
            curr_speed = curr_vel.speed
            
            if prev_speed == 0:
                continue
            
            # Calculate speed change percentage
            speed_change = abs(curr_speed - prev_speed) / prev_speed
            
            if speed_change > self.speed_change_threshold:
                anomalies.append(AnomalyType.SUDDEN_SPEED_CHANGE)
        
        return anomalies
    
    def _detect_unusual_acceleration(
        self,
        velocities: List[Velocity],
        timestamps: List[float]
    ) -> List[AnomalyType]:
        """Detect unusual acceleration patterns."""
        anomalies = []
        
        for i in range(1, len(velocities)):
            prev_vel = velocities[i-1]
            curr_vel = velocities[i]
            
            # Calculate velocity change
            dvx = curr_vel.vx - prev_vel.vx
            dvy = curr_vel.vy - prev_vel.vy
            dvz = curr_vel.vz - prev_vel.vz
            velocity_change = math.sqrt(dvx**2 + dvy**2 + dvz**2)
            
            # Calculate time delta
            dt = timestamps[i] - timestamps[i-1]
            if dt <= 0:
                dt = 1.0
            
            # Calculate acceleration
            acceleration = velocity_change / dt
            
            if acceleration > self.acceleration_threshold:
                anomalies.append(AnomalyType.UNUSUAL_ACCELERATION)
        
        return anomalies
    
    def _detect_unusual_trajectory(
        self,
        positions: List[Coordinates],
        timestamps: List[float]
    ) -> List[AnomalyType]:
        """Detect unusual trajectory patterns."""
        anomalies = []
        
        if len(positions) < 3:
            return anomalies
        
        # Check for non-smooth trajectory (large curvature changes)
        for i in range(1, len(positions) - 1):
            prev_pos = positions[i-1]
            curr_pos = positions[i]
            next_pos = positions[i+1]
            
            # Calculate vectors
            v1 = Coordinates(
                x=curr_pos.x - prev_pos.x,
                y=curr_pos.y - prev_pos.y,
                z=curr_pos.z - prev_pos.z
            )
            v2 = Coordinates(
                x=next_pos.x - curr_pos.x,
                y=next_pos.y - curr_pos.y,
                z=next_pos.z - curr_pos.z
            )
            
            # Calculate angle between vectors
            v1_mag = math.sqrt(v1.x**2 + v1.y**2 + v1.z**2)
            v2_mag = math.sqrt(v2.x**2 + v2.y**2 + v2.z**2)
            
            if v1_mag == 0 or v2_mag == 0:
                continue
            
            dot_product = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z
            cos_angle = dot_product / (v1_mag * v2_mag)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle = math.acos(cos_angle)
            
            # Large angle indicates sharp turn (unusual trajectory)
            if angle > math.pi / 3:  # 60 degrees
                anomalies.append(AnomalyType.UNUSUAL_TRAJECTORY)
                break  # Only flag once per trajectory
        
        return anomalies
    
    def _generate_reasoning(
        self,
        anomalies: List[AnomalyType],
        anomaly_score: float
    ) -> str:
        """Generate human-readable reasoning for anomalies."""
        reasoning_parts = []
        
        if len(anomalies) == 0:
            reasoning_parts.append("No anomalies detected. Motion appears normal.")
        else:
            reasoning_parts.append(f"Anomalies detected: {len(anomalies)}")
            for anomaly in anomalies:
                reasoning_parts.append(f"  - {anomaly.value}")
            reasoning_parts.append(f"Anomaly score: {anomaly_score:.2f}")
        
        reasoning_parts.append("")
        reasoning_parts.append("IMPORTANT: Anomalies do NOT imply hostile intent.")
        reasoning_parts.append("They indicate unusual motion patterns that may require investigation.")
        
        return "\n".join(reasoning_parts)

