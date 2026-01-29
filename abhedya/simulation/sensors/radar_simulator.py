"""
Radar Sensor Simulator

Mathematical simulation of radar sensor for detecting and tracking
aerial entities. Provides radar-style positional data with realistic
noise and uncertainty modeling.
"""

import math
from datetime import datetime
from typing import List, Optional, Dict, Any

from abhedya.domain.value_objects import Coordinates, Velocity
from abhedya.domain.enums import SensorType
from abhedya.simulation.models.entity import SimulatedEntity
from abhedya.simulation.models.noise import NoiseModel, NoiseParameters
from abhedya.infrastructure.config.config import SensorConfiguration


class RadarSimulator:
    """
    Radar sensor simulator for mathematical simulation of radar detection.
    
    Provides:
    - Position detection with noise
    - Velocity measurement with noise
    - Signal strength calculation based on distance and RCS
    - Detection confidence assessment
    - Timestamped, structured output
    """
    
    def __init__(
        self,
        sensor_id: str,
        sensor_position: Coordinates,
        detection_range_meters: float = None,
        update_rate_hertz: float = None,
        noise_parameters: Optional[NoiseParameters] = None,
        random_seed: Optional[int] = None
    ):
        """
        Initialize radar simulator.
        
        Args:
            sensor_id: Unique sensor identifier
            sensor_position: Position of the radar sensor
            detection_range_meters: Maximum detection range (default from config)
            update_rate_hertz: Update rate in Hz (default from config)
            noise_parameters: Noise model parameters (default from config)
            random_seed: Random seed for deterministic behavior
        """
        self.sensor_id = sensor_id
        self.sensor_position = sensor_position
        self.detection_range_meters = (
            detection_range_meters or
            SensorConfiguration.DEFAULT_RADAR_RANGE_METERS
        )
        self.update_rate_hertz = (
            update_rate_hertz or
            SensorConfiguration.DEFAULT_RADAR_UPDATE_RATE_HERTZ
        )
        
        # Initialize noise model
        if noise_parameters is None:
            noise_parameters = NoiseParameters(
                position_noise_standard_deviation_meters=(
                    SensorConfiguration.RADAR_POSITION_NOISE_STANDARD_DEVIATION_METERS
                ),
                velocity_noise_standard_deviation_meters_per_second=(
                    SensorConfiguration.RADAR_VELOCITY_NOISE_STANDARD_DEVIATION_METERS_PER_SECOND
                ),
                signal_strength_noise_standard_deviation=0.1,
                random_seed=random_seed
            )
        
        self.noise_model = NoiseModel(noise_parameters)
        self._last_update_time: Optional[datetime] = None
    
    def detect_entities(
        self,
        timestamp: datetime,
        entities: List[SimulatedEntity]
    ) -> List[Dict[str, Any]]:
        """
        Simulate radar detection of entities.
        
        Args:
            timestamp: Current timestamp
            entities: List of simulated entities to detect
            
        Returns:
            List of detection dictionaries with structured data
        """
        # Rate limiting
        if self._last_update_time is not None:
            time_delta = (timestamp - self._last_update_time).total_seconds()
            min_interval = 1.0 / self.update_rate_hertz
            if time_delta < min_interval:
                return []  # Too soon for next update
        
        self._last_update_time = timestamp
        
        detections = []
        
        for entity in entities:
            # Get true position and velocity
            true_position = entity.get_position_at_time(timestamp)
            true_velocity = entity.get_velocity_at_time(timestamp)
            
            # Calculate distance from sensor
            distance = self._calculate_distance(true_position)
            
            # Check if entity is within detection range
            if distance > self.detection_range_meters:
                continue
            
            # Calculate signal strength based on RCS and distance
            signal_strength = self.noise_model.calculate_signal_strength(
                distance_from_sensor=distance,
                radar_cross_section=entity.characteristics.radar_cross_section
            )
            
            # Calculate detection confidence
            confidence = self.noise_model.calculate_detection_confidence(
                distance_from_sensor=distance,
                signal_strength=signal_strength,
                maximum_detection_range=self.detection_range_meters
            )
            
            # Check if detection meets minimum confidence threshold
            from abhedya.infrastructure.config.config import ConfidenceThresholds
            if confidence < ConfidenceThresholds.MINIMUM_SENSOR_DETECTION_CONFIDENCE:
                continue  # Confidence too low, skip detection
            
            # Add noise to position and velocity
            noisy_position = self.noise_model.add_position_noise(
                true_position=true_position,
                distance_from_sensor=distance
            )
            
            noisy_velocity = self.noise_model.add_velocity_noise(
                true_velocity=true_velocity,
                distance_from_sensor=distance
            )
            
            # Calculate measurement uncertainty
            uncertainty = self.noise_model.calculate_measurement_uncertainty(
                distance_from_sensor=distance,
                signal_strength=signal_strength
            )
            
            # Create structured detection output
            detection = {
                "sensor_id": self.sensor_id,
                "sensor_type": SensorType.RADAR.value,
                "timestamp": timestamp.isoformat(),
                "entity_id": entity.entity_id,
                "position": {
                    "x": noisy_position.x,
                    "y": noisy_position.y,
                    "z": noisy_position.z,
                    "true_x": true_position.x,  # For validation/debugging
                    "true_y": true_position.y,
                    "true_z": true_position.z,
                },
                "velocity": {
                    "vx": noisy_velocity.vx,
                    "vy": noisy_velocity.vy,
                    "vz": noisy_velocity.vz,
                    "true_vx": true_velocity.vx,  # For validation/debugging
                    "true_vy": true_velocity.vy,
                    "true_vz": true_velocity.vz,
                },
                "signal_strength": signal_strength,
                "confidence": confidence,
                "uncertainty": uncertainty,
                "distance_from_sensor_meters": distance,
                "metadata": {
                    "entity_type": entity.characteristics.entity_type.value,
                    "radar_cross_section": entity.characteristics.radar_cross_section,
                    "size_category": entity.characteristics.size_category,
                }
            }
            
            detections.append(detection)
        
        return detections
    
    def _calculate_distance(self, position: Coordinates) -> float:
        """
        Calculate distance from sensor to position.
        
        Args:
            position: Target position
            
        Returns:
            Distance in meters
        """
        dx = position.x - self.sensor_position.x
        dy = position.y - self.sensor_position.y
        dz = position.z - self.sensor_position.z
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def get_sensor_info(self) -> Dict[str, Any]:
        """
        Get sensor information.
        
        Returns:
            Dictionary with sensor information
        """
        return {
            "sensor_id": self.sensor_id,
            "sensor_type": SensorType.RADAR.value,
            "position": {
                "x": self.sensor_position.x,
                "y": self.sensor_position.y,
                "z": self.sensor_position.z,
            },
            "detection_range_meters": self.detection_range_meters,
            "update_rate_hertz": self.update_rate_hertz,
        }

