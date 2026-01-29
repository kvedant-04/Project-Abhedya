"""
Tracking State Data Models

Data models for track state, classification results, and track identifiers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from abhedya.domain.value_objects import Coordinates, Velocity


class ObjectType(str, Enum):
    """Classified object types."""
    AERIAL_DRONE = "AERIAL_DRONE"
    AIRCRAFT = "AIRCRAFT"
    UNKNOWN_OBJECT = "UNKNOWN_OBJECT"


class TrackState(str, Enum):
    """Track state enumeration."""
    INITIALIZING = "INITIALIZING"  # Track being initialized
    ACTIVE = "ACTIVE"               # Active track
    COASTING = "COASTING"           # Track without recent updates
    TERMINATED = "TERMINATED"       # Terminated track


@dataclass
class ClassificationResult:
    """
    Probabilistic classification result.
    
    Includes classification probabilities and uncertainty.
    """
    object_type: ObjectType
    probability: float  # Probability of this classification [0.0, 1.0]
    uncertainty: float  # Classification uncertainty [0.0, 1.0]
    probabilities: Dict[ObjectType, float]  # Probabilities for all types
    reasoning: str  # Explanation of classification
    
    def __post_init__(self):
        """Validate classification result."""
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(f"Probability must be in [0.0, 1.0], got {self.probability}")
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be in [0.0, 1.0], got {self.uncertainty}")


@dataclass
class TrackIdentifier:
    """
    Unique and persistent track identifier.
    """
    track_id: str
    created_at: datetime
    last_updated: datetime
    update_count: int = 0
    
    def update(self):
        """Update track identifier timestamp and count."""
        self.last_updated = datetime.now()
        self.update_count += 1


@dataclass
class Track:
    """
    Track representing a detected and tracked object.
    
    Contains state, classification, and tracking information.
    """
    identifier: TrackIdentifier
    state: TrackState
    position: Coordinates
    velocity: Optional[Velocity]
    classification: ClassificationResult
    confidence: float  # Track confidence [0.0, 1.0]
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate track data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {self.confidence}")
    
    def update(
        self,
        position: Coordinates,
        velocity: Optional[Velocity] = None,
        classification: Optional[ClassificationResult] = None,
        confidence: Optional[float] = None
    ):
        """
        Update track with new measurements.
        
        Args:
            position: New position
            velocity: New velocity (optional)
            classification: New classification (optional)
            confidence: New confidence (optional)
        """
        self.position = position
        if velocity is not None:
            self.velocity = velocity
        if classification is not None:
            self.classification = classification
        if confidence is not None:
            if not 0.0 <= confidence <= 1.0:
                raise ValueError(f"Confidence must be in [0.0, 1.0], got {confidence}")
            self.confidence = confidence
        
        self.last_updated = datetime.now()
        self.identifier.update()
    
    def get_age_seconds(self) -> float:
        """
        Get track age in seconds.
        
        Returns:
            Age in seconds
        """
        return (datetime.now() - self.created_at).total_seconds()
    
    def get_time_since_update_seconds(self) -> float:
        """
        Get time since last update in seconds.
        
        Returns:
            Time since last update in seconds
        """
        return (datetime.now() - self.last_updated).total_seconds()
    
    def is_stale(self, max_age_seconds: float = 60.0) -> bool:
        """
        Check if track is stale (no recent updates).
        
        Args:
            max_age_seconds: Maximum age without updates
            
        Returns:
            True if track is stale
        """
        return self.get_time_since_update_seconds() > max_age_seconds

