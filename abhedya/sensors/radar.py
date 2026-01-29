"""
Radar sensor simulation.

Simulates a primary radar system for detecting and tracking
airborne entities.
"""

import random
import math
from datetime import datetime
from typing import List, Optional

from abhedya.sensors.base import BaseSensor
from abhedya.core.models import (
    SensorReading,
    SensorType,
    Coordinates,
    Velocity
)


class RadarSensor(BaseSensor):
    """Primary radar sensor simulation."""
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        position: Optional[Coordinates] = None,
        range_meters: float = 150000.0,  # 150 km typical radar range
        update_rate_hz: float = 1.0,
        detection_threshold: float = 0.4,
        scan_pattern: str = "360"  # "360" for full scan, "sector" for sector scan
    ):
        """
        Initialize radar sensor.
        
        Args:
            sensor_id: Unique sensor identifier
            position: Sensor position
            range_meters: Maximum detection range
            update_rate_hz: Update rate
            detection_threshold: Minimum detection confidence
            scan_pattern: Scan pattern type
        """
        super().__init__(
            sensor_id=sensor_id,
            position=position,
            range_meters=range_meters,
            update_rate_hz=update_rate_hz,
            detection_threshold=detection_threshold
        )
        self.scan_pattern = scan_pattern
        self._simulated_entities = []  # For simulation purposes
    
    def get_sensor_type(self) -> str:
        """Return sensor type."""
        return SensorType.RADAR.value
    
    def add_simulated_entity(
        self,
        position: Coordinates,
        velocity: Optional[Velocity] = None,
        entity_id: Optional[str] = None
    ):
        """
        Add a simulated entity for detection (for testing/simulation).
        
        Args:
            position: Entity position
            velocity: Entity velocity
            entity_id: Optional entity identifier
        """
        self._simulated_entities.append({
            "id": entity_id or f"entity_{len(self._simulated_entities)}",
            "position": position,
            "velocity": velocity
        })
    
    def clear_simulated_entities(self):
        """Clear all simulated entities."""
        self._simulated_entities = []
    
    def _detect_entities(self, timestamp: datetime) -> List[SensorReading]:
        """
        Simulate radar detection of entities.
        
        In a real system, this would interface with actual radar hardware.
        Here, we simulate detection of entities within range.
        """
        readings = []
        
        for entity in self._simulated_entities:
            # Calculate distance
            distance = self._calculate_distance(entity["position"])
            
            if distance > self.range_meters:
                continue
            
            # Calculate signal strength (radar cross-section dependent)
            signal_strength = self._calculate_signal_strength(
                distance,
                base_strength=0.8  # Typical aircraft RCS
            )
            
            # Calculate detection confidence
            confidence = self._calculate_detection_confidence(
                distance,
                signal_strength
            )
            
            # Add realistic measurement noise
            noisy_position = self._add_position_noise(
                entity["position"],
                distance
            )
            
            noisy_velocity = None
            if entity["velocity"]:
                noisy_velocity = self._add_velocity_noise(
                    entity["velocity"]
                )
            
            # Create sensor reading
            reading = SensorReading(
                sensor_id=self._sensor_id,
                sensor_type=SensorType.RADAR,
                timestamp=timestamp,
                position=noisy_position,
                velocity=noisy_velocity,
                signal_strength=signal_strength,
                confidence=confidence,
                metadata={
                    "entity_id": entity["id"],
                    "distance_meters": distance,
                    "scan_pattern": self.scan_pattern
                }
            )
            
            readings.append(reading)
        
        return readings
    
    def _add_position_noise(
        self,
        true_position: Coordinates,
        distance: float
    ) -> Coordinates:
        """
        Add realistic radar measurement noise to position.
        
        Noise increases with distance.
        """
        # Noise standard deviation increases with distance
        noise_std = 50.0 + (distance / 1000.0) * 10.0  # meters
        
        return Coordinates(
            x=true_position.x + random.gauss(0.0, noise_std),
            y=true_position.y + random.gauss(0.0, noise_std),
            z=true_position.z + random.gauss(0.0, noise_std * 0.5)  # Less noise in altitude
        )
    
    def _add_velocity_noise(self, true_velocity: Velocity) -> Velocity:
        """Add realistic velocity measurement noise."""
        noise_std = 5.0  # m/s
        
        return Velocity(
            vx=true_velocity.vx + random.gauss(0.0, noise_std),
            vy=true_velocity.vy + random.gauss(0.0, noise_std),
            vz=true_velocity.vz + random.gauss(0.0, noise_std * 0.5)
        )

