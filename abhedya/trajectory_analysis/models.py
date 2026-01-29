"""
Trajectory Analysis Data Models

Data models for trajectory predictions, physics validation,
anomaly detection, and proximity estimates.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from abhedya.domain.value_objects import Coordinates, Velocity


class MotionModel(str, Enum):
    """Motion models for trajectory prediction."""
    CONSTANT_VELOCITY = "CONSTANT_VELOCITY"
    CONSTANT_ACCELERATION = "CONSTANT_ACCELERATION"


class PhysicsViolationType(str, Enum):
    """Types of physics violations."""
    EXCESSIVE_ACCELERATION = "EXCESSIVE_ACCELERATION"
    EXCESSIVE_SPEED = "EXCESSIVE_SPEED"
    IMPOSSIBLE_VELOCITY_CHANGE = "IMPOSSIBLE_VELOCITY_CHANGE"
    IMPOSSIBLE_POSITION_CHANGE = "IMPOSSIBLE_POSITION_CHANGE"
    INVALID_ACCELERATION = "INVALID_ACCELERATION"


class AnomalyType(str, Enum):
    """Types of motion anomalies."""
    SUDDEN_DIRECTION_CHANGE = "SUDDEN_DIRECTION_CHANGE"
    SUDDEN_SPEED_CHANGE = "SUDDEN_SPEED_CHANGE"
    UNUSUAL_ACCELERATION = "UNUSUAL_ACCELERATION"
    UNUSUAL_TRAJECTORY = "UNUSUAL_TRAJECTORY"
    PHYSICS_VIOLATION = "PHYSICS_VIOLATION"


@dataclass
class TrajectoryPrediction:
    """Trajectory prediction result."""
    current_position: Coordinates
    current_velocity: Velocity
    predicted_positions: List[Coordinates]  # Positions at future time steps
    time_steps: List[float]  # Time steps in seconds
    motion_model: MotionModel
    confidence: float  # Prediction confidence [0.0, 1.0]
    uncertainty: float  # Prediction uncertainty [0.0, 1.0]
    timestamp: datetime


@dataclass
class PhysicsValidationResult:
    """Physics validation result."""
    is_valid: bool
    violations: List[PhysicsViolationType]
    max_acceleration: float  # Maximum acceleration observed (m/s²)
    max_speed: float  # Maximum speed observed (m/s)
    average_acceleration: float  # Average acceleration (m/s²)
    reasoning: str  # Explanation of validation


@dataclass
class AnomalyDetectionResult:
    """Anomaly detection result."""
    is_anomalous: bool
    anomaly_types: List[AnomalyType]
    anomaly_score: float  # Anomaly score [0.0, 1.0]
    reasoning: str  # Explanation of anomaly
    note: str  # Important: Anomalies do NOT imply hostile intent


@dataclass
class ProximityEstimate:
    """Time-to-proximity estimate for protected zones."""
    zone_name: str
    zone_radius_meters: float
    current_distance_meters: float
    estimated_time_to_proximity_seconds: Optional[float]  # None if not approaching
    is_approaching: bool
    approach_velocity_meters_per_second: float
    confidence: float  # Estimate confidence [0.0, 1.0]
    timestamp: datetime

