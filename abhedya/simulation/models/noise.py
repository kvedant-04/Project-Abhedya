"""
Noise and Uncertainty Models

Mathematical models for simulating sensor noise and measurement uncertainty
in a controlled, deterministic manner.
"""

import math
import random
from typing import Tuple, Optional
from dataclasses import dataclass

from abhedya.domain.value_objects import Coordinates, Velocity


@dataclass
class NoiseParameters:
    """
    Parameters for noise generation.
    """
    position_noise_standard_deviation_meters: float
    velocity_noise_standard_deviation_meters_per_second: float
    signal_strength_noise_standard_deviation: float
    random_seed: Optional[int] = None
    
    def __post_init__(self):
        """Initialize random seed if provided."""
        if self.random_seed is not None:
            random.seed(self.random_seed)


class NoiseModel:
    """
    Mathematical noise model for sensor measurements.
    Uses Gaussian (normal) distribution for realistic noise modeling.
    """
    
    def __init__(self, parameters: NoiseParameters):
        """
        Initialize noise model.
        
        Args:
            parameters: Noise parameters
        """
        self.parameters = parameters
        if parameters.random_seed is not None:
            self.random_state = random.Random(parameters.random_seed)
        else:
            self.random_state = random.Random()
    
    def add_position_noise(
        self,
        true_position: Coordinates,
        distance_from_sensor: float
    ) -> Coordinates:
        """
        Add realistic position measurement noise.
        
        Noise increases with distance from sensor (inverse square law effect).
        
        Args:
            true_position: True position of entity
            distance_from_sensor: Distance from sensor in meters
            
        Returns:
            Position with added noise
        """
        # Noise increases with distance
        distance_factor = 1.0 + (distance_from_sensor / 100000.0)  # Scale factor
        
        noise_std = (
            self.parameters.position_noise_standard_deviation_meters *
            distance_factor
        )
        
        # Add Gaussian noise to each coordinate
        noise_x = self.random_state.gauss(0.0, noise_std)
        noise_y = self.random_state.gauss(0.0, noise_std)
        noise_z = self.random_state.gauss(0.0, noise_std * 0.5)  # Less noise in altitude
        
        return Coordinates(
            x=true_position.x + noise_x,
            y=true_position.y + noise_y,
            z=true_position.z + noise_z
        )
    
    def add_velocity_noise(
        self,
        true_velocity: Velocity,
        distance_from_sensor: float
    ) -> Velocity:
        """
        Add realistic velocity measurement noise.
        
        Args:
            true_velocity: True velocity of entity
            distance_from_sensor: Distance from sensor in meters
            
        Returns:
            Velocity with added noise
        """
        # Velocity noise is less affected by distance than position
        distance_factor = 1.0 + (distance_from_sensor / 200000.0)
        
        noise_std = (
            self.parameters.velocity_noise_standard_deviation_meters_per_second *
            distance_factor
        )
        
        noise_vx = self.random_state.gauss(0.0, noise_std)
        noise_vy = self.random_state.gauss(0.0, noise_std)
        noise_vz = self.random_state.gauss(0.0, noise_std * 0.5)
        
        return Velocity(
            vx=true_velocity.vx + noise_vx,
            vy=true_velocity.vy + noise_vy,
            vz=true_velocity.vz + noise_vz
        )
    
    def calculate_signal_strength(
        self,
        distance_from_sensor: float,
        radar_cross_section: float,
        base_signal_strength: float = 1.0
    ) -> float:
        """
        Calculate signal strength based on distance and RCS.
        
        Uses inverse square law with noise.
        
        Args:
            distance_from_sensor: Distance from sensor in meters
            radar_cross_section: Radar cross section (0.0 to 1.0)
            base_signal_strength: Base signal strength
            
        Returns:
            Signal strength (0.0 to 1.0)
        """
        if distance_from_sensor <= 0:
            return base_signal_strength * radar_cross_section
        
        # Inverse square law
        distance_factor = 1.0 / (1.0 + (distance_from_sensor / 10000.0)**2)
        
        # Apply RCS
        signal_strength = base_signal_strength * radar_cross_section * distance_factor
        
        # Add noise
        noise = self.random_state.gauss(0.0, self.parameters.signal_strength_noise_standard_deviation)
        signal_strength = signal_strength + noise
        
        # Clamp to valid range
        return max(0.0, min(1.0, signal_strength))
    
    def calculate_detection_confidence(
        self,
        distance_from_sensor: float,
        signal_strength: float,
        maximum_detection_range: float
    ) -> float:
        """
        Calculate detection confidence based on distance and signal strength.
        
        Args:
            distance_from_sensor: Distance from sensor in meters
            signal_strength: Signal strength (0.0 to 1.0)
            maximum_detection_range: Maximum detection range in meters
            
        Returns:
            Detection confidence (0.0 to 1.0)
        """
        # Confidence decreases with distance
        distance_factor = max(0.0, 1.0 - (distance_from_sensor / maximum_detection_range))
        
        # Confidence increases with signal strength
        signal_factor = signal_strength
        
        # Combined confidence (weighted average)
        confidence = (distance_factor * 0.6) + (signal_factor * 0.4)
        
        # Add small random variation
        noise = self.random_state.gauss(0.0, 0.05)
        confidence = confidence + noise
        
        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
    
    def calculate_measurement_uncertainty(
        self,
        distance_from_sensor: float,
        signal_strength: float
    ) -> float:
        """
        Calculate measurement uncertainty.
        
        Args:
            distance_from_sensor: Distance from sensor in meters
            signal_strength: Signal strength (0.0 to 1.0)
            
        Returns:
            Uncertainty value (0.0 to 1.0, higher = more uncertain)
        """
        # Uncertainty increases with distance
        distance_uncertainty = min(1.0, distance_from_sensor / 200000.0)
        
        # Uncertainty increases with low signal strength
        signal_uncertainty = 1.0 - signal_strength
        
        # Combined uncertainty
        uncertainty = (distance_uncertainty * 0.7) + (signal_uncertainty * 0.3)
        
        return max(0.0, min(1.0, uncertainty))


class DeterministicNoiseModel(NoiseModel):
    """
    Deterministic noise model that uses a fixed random seed for reproducible results.
    """
    
    def __init__(
        self,
        parameters: NoiseParameters,
        seed: Optional[int] = None
    ):
        """
        Initialize deterministic noise model.
        
        Args:
            parameters: Noise parameters
            seed: Random seed for deterministic behavior
        """
        if seed is not None:
            parameters.random_seed = seed
        super().__init__(parameters)

