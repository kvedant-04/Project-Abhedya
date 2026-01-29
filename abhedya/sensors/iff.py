"""
IFF (Identification Friend or Foe) sensor simulation.

Simulates IFF transponder interrogation and response system
for identifying friendly entities.
"""

import random
from datetime import datetime
from typing import List, Optional, Dict

from abhedya.sensors.base import BaseSensor
from abhedya.core.models import (
    SensorReading,
    SensorType,
    Coordinates,
    Velocity
)


class IFFSensor(BaseSensor):
    """IFF transponder interrogation sensor."""
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        position: Optional[Coordinates] = None,
        range_meters: float = 200000.0,  # IFF typically has longer range than radar
        update_rate_hz: float = 2.0,  # Higher update rate for IFF
        detection_threshold: float = 0.6,
        friendly_codes: Optional[Dict[str, str]] = None
    ):
        """
        Initialize IFF sensor.
        
        Args:
            sensor_id: Unique sensor identifier
            position: Sensor position
            range_meters: Maximum interrogation range
            update_rate_hz: Update rate
            detection_threshold: Minimum confidence
            friendly_codes: Dictionary mapping entity IDs to IFF codes
        """
        super().__init__(
            sensor_id=sensor_id,
            position=position,
            range_meters=range_meters,
            update_rate_hz=update_rate_hz,
            detection_threshold=detection_threshold
        )
        self.friendly_codes = friendly_codes or {}
        self._simulated_entities = []
    
    def get_sensor_type(self) -> str:
        """Return sensor type."""
        return SensorType.IFF.value
    
    def add_simulated_entity(
        self,
        position: Coordinates,
        velocity: Optional[Velocity] = None,
        entity_id: Optional[str] = None,
        iff_code: Optional[str] = None,
        is_friendly: bool = False
    ):
        """
        Add simulated entity with IFF characteristics.
        
        Args:
            position: Entity position
            velocity: Entity velocity
            entity_id: Entity identifier
            iff_code: IFF transponder code
            is_friendly: Whether entity is friendly
        """
        self._simulated_entities.append({
            "id": entity_id or f"entity_{len(self._simulated_entities)}",
            "position": position,
            "velocity": velocity,
            "iff_code": iff_code,
            "is_friendly": is_friendly
        })
        
        if is_friendly and iff_code:
            self.friendly_codes[entity_id or f"entity_{len(self._simulated_entities) - 1}"] = iff_code
    
    def clear_simulated_entities(self):
        """Clear all simulated entities."""
        self._simulated_entities = []
    
    def _detect_entities(self, timestamp: datetime) -> List[SensorReading]:
        """
        Simulate IFF interrogation and response.
        
        IFF provides positive identification for friendly entities
        and no response (or negative response) for others.
        """
        readings = []
        
        for entity in self._simulated_entities:
            distance = self._calculate_distance(entity["position"])
            
            if distance > self.range_meters:
                continue
            
            # IFF response characteristics
            if entity.get("is_friendly") and entity.get("iff_code"):
                # Friendly entity with valid IFF code
                signal_strength = self._calculate_signal_strength(
                    distance,
                    base_strength=0.9  # Strong IFF response
                )
                confidence = 0.95  # High confidence for valid IFF response
                iff_response = "FRIENDLY"
            elif entity.get("iff_code"):
                # Entity with IFF but not in friendly codes
                signal_strength = self._calculate_signal_strength(
                    distance,
                    base_strength=0.5
                )
                confidence = 0.7
                iff_response = "UNKNOWN_CODE"
            else:
                # No IFF response
                signal_strength = self._calculate_signal_strength(
                    distance,
                    base_strength=0.2
                )
                confidence = 0.3
                iff_response = "NO_RESPONSE"
            
            # IFF typically provides better position accuracy than radar
            noisy_position = self._add_position_noise(
                entity["position"],
                distance,
                noise_scale=0.3  # Less noise than radar
            )
            
            noisy_velocity = None
            if entity["velocity"]:
                noisy_velocity = self._add_velocity_noise(
                    entity["velocity"],
                    noise_scale=0.3
                )
            
            reading = SensorReading(
                sensor_id=self._sensor_id,
                sensor_type=SensorType.IFF,
                timestamp=timestamp,
                position=noisy_position,
                velocity=noisy_velocity,
                signal_strength=signal_strength,
                confidence=confidence,
                metadata={
                    "entity_id": entity["id"],
                    "distance_meters": distance,
                    "iff_response": iff_response,
                    "iff_code": entity.get("iff_code"),
                    "is_friendly": entity.get("is_friendly", False)
                }
            )
            
            readings.append(reading)
        
        return readings
    
    def _add_position_noise(
        self,
        true_position: Coordinates,
        distance: float,
        noise_scale: float = 1.0
    ) -> Coordinates:
        """Add IFF position measurement noise."""
        noise_std = (50.0 + (distance / 1000.0) * 10.0) * noise_scale
        
        return Coordinates(
            x=true_position.x + random.gauss(0.0, noise_std),
            y=true_position.y + random.gauss(0.0, noise_std),
            z=true_position.z + random.gauss(0.0, noise_std * 0.5)
        )
    
    def _add_velocity_noise(
        self,
        true_velocity: Velocity,
        noise_scale: float = 1.0
    ) -> Velocity:
        """Add IFF velocity measurement noise."""
        noise_std = 5.0 * noise_scale
        
        return Velocity(
            vx=true_velocity.vx + random.gauss(0.0, noise_std),
            vy=true_velocity.vy + random.gauss(0.0, noise_std),
            vz=true_velocity.vz + random.gauss(0.0, noise_std * 0.5)
        )

