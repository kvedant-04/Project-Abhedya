"""
Trajectory Prediction and Physics Validation Engine

Provides:
- Short-term future position prediction
- Motion validation using classical physics constraints
- Detection of physically implausible or anomalous motion
- Time-to-proximity estimation for protected zones

All analysis uses classical mechanics only.
Anomalies do NOT imply hostile intent.
"""

from abhedya.trajectory_analysis.predictor import TrajectoryPredictor
from abhedya.trajectory_analysis.physics_validator import PhysicsValidator
from abhedya.trajectory_analysis.anomaly_detector import AnomalyDetector
from abhedya.trajectory_analysis.proximity_calculator import ProximityCalculator
from abhedya.trajectory_analysis.models import (
    TrajectoryPrediction,
    PhysicsValidationResult,
    AnomalyDetectionResult,
    ProximityEstimate
)

__all__ = [
    "TrajectoryPredictor",
    "PhysicsValidator",
    "AnomalyDetector",
    "ProximityCalculator",
    "TrajectoryPrediction",
    "PhysicsValidationResult",
    "AnomalyDetectionResult",
    "ProximityEstimate",
]

