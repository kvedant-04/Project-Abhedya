"""
Target Detection and Tracking Module

Provides:
- Probabilistic classification (Aerial Drone, Aircraft, Unknown Object)
- Multi-target tracking
- Unique and persistent track identifiers
- State estimation using Kalman Filters

All logic is explainable and uses classical mathematical techniques only.
"""

from abhedya.tracking.tracker import MultiTargetTracker
from abhedya.tracking.models import (
    Track,
    TrackState,
    ClassificationResult,
    TrackIdentifier
)
from abhedya.tracking.classifier import ProbabilisticClassifier
from abhedya.tracking.kalman import KalmanFilter, KalmanState

__all__ = [
    "MultiTargetTracker",
    "Track",
    "TrackState",
    "ClassificationResult",
    "TrackIdentifier",
    "ProbabilisticClassifier",
    "KalmanFilter",
    "KalmanState",
]

