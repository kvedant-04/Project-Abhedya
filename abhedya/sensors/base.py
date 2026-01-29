"""
Base sensor implementation.

Provides common functionality for all sensor types.
"""

import uuid
from datetime import datetime
from typing import List, Optional
import math

from abhedya.core.interfaces import ISensor
from abhedya.core.models import (
    SensorReading,
    SensorType,
    Coordinates,
    Velocity
)
from abhedya.core.constants import (
    DEFAULT_SENSOR_RANGE,
    DEFAULT_SENSOR_UPDATE_RATE,
    DEFAULT_DETECTION_CONFIDENCE_THRESHOLD
)


class BaseSensor(ISensor):
    """Base class for all sensor implementations."""
    
    def __init__(
        self,
        sensor_id: Optional[str] = None,
        position: Optional[Coordinates] = None,
        range_meters: float = DEFAULT_SENSOR_RANGE,
        update_rate_hz: float = DEFAULT_SENSOR_UPDATE_RATE,
        detection_threshold: float = DEFAULT_DETECTION_CONFIDENCE_THRESHOLD
    ):
        """
        Initialize base sensor.
        
        Args:
            sensor_id: Unique sensor identifier (auto-generated if None)
            position: Sensor position (defaults to origin)
            range_meters: Maximum detection range in meters
            update_rate_hz: Sensor update rate in Hz
            detection_threshold: Minimum confidence for detection
        """
        self._sensor_id = sensor_id or f"sensor_{uuid.uuid4().hex[:8]}"
        self.position = position or Coordinates(x=0.0, y=0.0, z=0.0)
        self.range_meters = range_meters
        self.update_rate_hz = update_rate_hz
        self.detection_threshold = detection_threshold
        self._last_update = None
    
    def get_sensor_id(self) -> str:
        """Return unique sensor identifier."""
        return self._sensor_id
    
    def get_sensor_type(self) -> str:
        """Return sensor type (must be implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement get_sensor_type")
    
    def detect(self, timestamp: datetime) -> List[SensorReading]:
        """
        Simulate sensor detection.
        
        Base implementation handles timing and basic filtering.
        Subclasses should implement _detect_entities().
        """
        # Rate limiting
        if self._last_update is not None:
            time_delta = (timestamp - self._last_update).total_seconds()
            min_interval = 1.0 / self.update_rate_hz
            if time_delta < min_interval:
                return []  # Too soon for next update
        
        self._last_update = timestamp
        
        # Get detections from subclass
        detections = self._detect_entities(timestamp)
        
        # Filter by range and confidence
        filtered = []
        for detection in detections:
            distance = self._calculate_distance(detection.position)
            if distance <= self.range_meters:
                if detection.confidence >= self.detection_threshold:
                    filtered.append(detection)
        
        return filtered
    
    def _detect_entities(self, timestamp: datetime) -> List[SensorReading]:
        """
        Detect entities (must be implemented by subclasses).
        
        Args:
            timestamp: Current timestamp
            
        Returns:
            List of sensor readings
        """
        raise NotImplementedError("Subclasses must implement _detect_entities")
    
    def _calculate_distance(self, position: Coordinates) -> float:
        """Calculate distance from sensor to position."""
        dx = position.x - self.position.x
        dy = position.y - self.position.y
        dz = position.z - self.position.z
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
    def _calculate_signal_strength(
        self,
        distance: float,
        base_strength: float = 1.0
    ) -> float:
        """
        Calculate signal strength based on distance.
        
        Uses inverse square law with noise.
        """
        import random
        
        if distance <= 0:
            return base_strength
        
        # Inverse square law
        strength = base_strength / (1.0 + (distance / 10000.0)**2)
        
        # Add realistic noise
        noise = random.gauss(0.0, 0.1)
        strength = max(0.0, min(1.0, strength + noise))
        
        return strength
    
    def _calculate_detection_confidence(
        self,
        distance: float,
        signal_strength: float
    ) -> float:
        """
        Calculate detection confidence based on distance and signal strength.
        """
        # Confidence decreases with distance
        distance_factor = max(0.0, 1.0 - (distance / self.range_meters))
        
        # Confidence increases with signal strength
        signal_factor = signal_strength
        
        # Combined confidence
        confidence = (distance_factor * 0.6 + signal_factor * 0.4)
        
        return max(0.0, min(1.0, confidence))

